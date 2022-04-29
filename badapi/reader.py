#!/usr/bin/env python
# coding: utf-8


import pandas as pd
import json
import requests
import functools
import re
from numpy import logical_or, logical_and, nan

from badapi.localization import Localization
from badapi.constants import *


def _split_bond_stat(df):
    # Check if all required columns are present
    needed_cols = ('FavorLevel', 'StatType', 'StatValue')
    if not all(header in df.columns for header in needed_cols):
        raise KeyError('Cannot find the appropriate columns labels', needed_cols, df.columns)
    
    
    # get the two bond stats by looking at the final row
    df_stat1, df_stat2 = df.StatType.iloc[-1]
    
    # map to familiar names
    df_stat1 = bond_stat_type_map[df_stat1]
    df_stat2 = bond_stat_type_map[df_stat2]
    
    # cumsum of stats 
    # str[0/1] access the first/second element of the list
    # non-existent entries are stored as NaN
    # fillna converts NaNs to 0
    # cast to int to make everything consistent
    # and finally convert to list
    df_stat1_value = df.StatValue.str[0].fillna(0).astype(int).cumsum().tolist()
    df_stat2_value = df.StatValue.str[1].fillna(0).astype(int).cumsum().tolist()
    
    # insert a 0 at the beginning for bond level 1
    df_stat1_value.insert(0, 0)
    df_stat2_value.insert(0, 0)

    return pd.DataFrame({'Stat1': df_stat1, 'Stat1Value': df_stat1_value, 'Stat2': df_stat2, 'Stat2Value': df_stat2_value})


# compile regex for splitting UE passive description
_re_split_ue_desc = re.compile(r'^(.+?)を\[c]\[007eff](\d+\.?\d*%?)\[-]\[\/c]増加\/\n.*')

def _parse_ue_passive_stats(df):
    # Check if all required columns are present
    needed_cols = ('CharacterId', 'DescriptionJp')
    if not all(header in df.columns for header in needed_cols):
        raise KeyError('Cannot find the appropriate columns labels', needed_cols, df.columns)
    
    # sort by level, ascending
    df.sort_values(by='Level', inplace=True)
    # regex magic to split skill description
    df2 = df.DescriptionJp.str.split(_re_split_ue_desc, expand=True)
    
    # get stat name from first element of second column
    # then use dictionary to map to English
    try:
        stat_name = jp_stat_name_map[df2.iloc[0, 1]]
        # convert stat values to a list
        stat_values = df2.iloc[:, 2].tolist()
    except IndexError:
        return 
    
    return pd.DataFrame({ "WeaponPassiveStatName": stat_name, "WeaponPassiveStatValue": stat_values })


# compile regex based on list of known stat names
_stat_names_joined = "|".join(jp_stat_name_map.keys())
_actions_joined = "|".join(action_map.keys())
# compile regex for splitting buff skill description
_re_skill_desc = re.compile(fr'({_stat_names_joined})(?:の|を|が)\[c]\[007eff](\d+\.?\d*%?)\[-]\[\/c].*?({_actions_joined})', flags=re.S)

def _parse_skill_desc(df):
    # Check if all required columns are present
    needed_cols = ('SkillCategory', 'DescriptionJp', 'SkillCost')
    if not all(header in df.columns for header in needed_cols):
        raise KeyError('Cannot find the appropriate columns labels', needed_cols, df.columns)
    
    # skill category
    category = df.SkillCategory.iloc[0]
    # sort by level, ascending
    df.sort_values(by='Level', inplace=True)
    # regex magic to split skill description
    df2 = df.DescriptionJp.str.split(_re_skill_desc, expand=True)
    
    # compute number of effects the skills has based on how many groups regex managed to capture
    df2_n_effects = (len(df2.columns) - 1) // 4
    # initialise list to store effects
    skill_effects = []
    for n in range(df2_n_effects):
        # temp dataframe
        d = df2[range(4*n+1, 4*n+4)]
        effect = {
            "SkillCategory": category,
            "Action": d.iloc[-1,2],
            "Status": d.iloc[-1,0],
            "Values": d.iloc[:,1].fillna('0%').tolist(), # need to fill null values with placeholder to avoid errors
            "Cost": df.SkillCost.fillna(0).tolist()
        }
        skill_effects.append(effect)
    
    return pd.DataFrame(skill_effects)


def _get_game_data(url):
    response = requests.get(url).json()
    data = pd.json_normalize(response['DataList'])

    return data    


class BAData:
    def __init__(self, url_root, url_global_root):
        """ Creates an instance of BA DataFrame by getting the required Excel tables from the repository root
        and then processing with Pandas
            
        :param url_root: URL of the root directory where the data tables are located. Make sure the tables are delivered in plain text
        """
        # fix url if is not a directory
        for u in (url_root, url_global_root):
            if ~u.endswith('/'):
                u += '/'

            # try if the url has some of the required files
            try:
                requests.get(u + "CharacterAcademyTagsExcelTable.json")
            except requests.exceptions.RequestException as err:
                print(f'Cannot find data tables from specified URL {u}')
                raise err
            
        self._url_root = url_root
        self._url_global_root = url_global_root

    def combine_localisation(self, table_name):
        """Combines JP and global localisation files for a particular localisation table
        
        :param table_name: name of the JSON file containing localisation data, common across both clients
        :return combined_table: the combined localisation table
        """
        # get jp and global localisation files
        loc_jp = _get_game_data(self._url_root + table_name)
        loc_gl = _get_game_data(self._url_global_root + table_name)
        
        # merge tables, using all the latest keys from JP
        loc_comb = pd.merge(loc_jp, loc_gl, how='left', on='Key', suffixes=[None, '_dupe'])
        loc_comb.fillna('', inplace=True)
        
        return loc_comb
    
    @functools.cached_property
    def character_stats(self):
        """Gets character stats table from the repo"""
        # fetch character stats
        chars_df = _get_game_data(self._url_root + "CharacterStatExcelTable.json")
        # rename columns with predefined dictionary
        chars_df = chars_df.rename(columns=character_stats_column_map)
        
        return chars_df
        
    @functools.cached_property
    def character_details(self):
        """Gets character details from the repo"""
        # get additional character details from other table
        details_df = _get_game_data(self._url_root + "CharacterExcelTable.json")
        # fix some damage type values
        details_df.BulletType = details_df.BulletType.replace(damage_type_map)
        details_df.ArmorType = details_df.BulletType.replace(armour_type_map)
        
        # localisation for character names
        localisation_df = self.combine_localisation("LocalizeEtcExcelTable.json")
        # backup names for ones that don't have english names yet
        backup_name_df = _get_game_data(self._url_root + "CharacterAcademyTagsExcelTable.json")[['Id', 'FavorItemUniqueTags']]
        backup_name_df['BackupName'] = backup_name_df['FavorItemUniqueTags'].map(lambda x: x[0].replace('F_', '').replace('_default', ''))
        
        # merge with localisation table for names
        details_df = details_df.merge(localisation_df, how='left', left_on='LocalizeEtcId', right_on='Key')
        details_df = details_df.merge(backup_name_df[['Id', 'BackupName']], how='left', on='Id', suffixes=[None,'_dupe'])
        details_df.BackupName.fillna("", inplace=True)
        
        # rename id to make joining easier
        # details_df = details_df.rename(columns={"Id": "CharacterId"})
        details_df['CharacterId'] = details_df['Id']
        
        return details_df
    
    @functools.cached_property
    def character_profiles(self):
        """Gets character profiles from the repo"""
        profiles_jp = _get_game_data(self._url_root + "LocalizeCharProfileExcelTable.json")
        profiles_gl = _get_game_data(self._url_global_root + "LocalizeCharProfileExcelTable.json")
        
        # merge tables, using all the latest keys from JP
        profiles_comb = pd.merge(profiles_jp, profiles_gl, how='left', on='CharacterId', suffixes=[None, '_dupe'])
        profiles_comb.fillna('', inplace=True)
        
        return profiles_comb
        
    @functools.cached_property
    def character_weapon(self):
        """Gets character UE stats from the repo"""
        # get most of the UE stats from the UE table
        ue_df = _get_game_data(self._url_root + "CharacterWeaponExcelTable.json")
        # fix terrain bonus text
        ue_df['TerrainBonus'] = ue_df.StatType.map(lambda x: adaptation_weapon_map[x[2]])
        # rename Id column to be more consistent
        ue_df = ue_df.rename(columns={"Id": "CharacterId"})
        
        return ue_df
    
    @functools.cached_property
    def character_bond_stats(self):
        """Gets character bond level stat bonuses"""
        # get character bond stats from game data
        bond_df = _get_game_data(self._url_root + "FavorLevelRewardExcelTable.json")
        # process the bond stat and then reset index to get CharacterId back
        bond_stats_df = bond_df.groupby('CharacterId').apply(_split_bond_stat).reset_index().rename(columns={ 'level_1': 'Level' })
        
        return bond_stats_df
    
    @functools.cached_property
    def character_skills(self):
        """Gets character skill data and localisation files"""
        # fetch the character skills data
        char_skill_df = _get_game_data(self._url_root + "CharacterSkillListExcelTable.json")
        # fetch the skill table
        skill_df = _get_game_data(self._url_root + "SkillExcelTable.json")
        # fetch the skill localisation table
        localisation_df = self.combine_localisation("LocalizeSkillExcelTable.json")
        
        # remove form conversion entries
        char_skill_df = char_skill_df[~char_skill_df['IsFormConversion']]
        # Rename the columns to more familiar names
        # EX -> EX, Public -> Normal, Passive -> Passive, ExtraPassive -> Sub
        char_skill_df = char_skill_df.rename(columns=skill_category_map)
        # massage the skill list into category + skill GroupId
        # melt the SkillGroupId column into long format
        char_skill_df = pd.melt(char_skill_df, id_vars=['CharacterId', 'MinimumGradeCharacterWeapon'],\
                                value_vars=list(skill_category_map.values()),\
                                var_name='SkillCategory', value_name='GroupId')
        # de-list the skill group ids with more pandas magic
        groups = char_skill_df.GroupId.apply(pd.Series, dtype=str).reset_index()\
                                        .melt(id_vars='index', var_name='dropme', value_name='GroupId')\
                                        .dropna()[['index', 'GroupId']]\
                                        .set_index('index')
        # remove entries with 'EmptySkill'
        groups = groups[groups.GroupId!='EmptySkill']
        # join with original DataFrame
        char_skill_df = char_skill_df.merge(groups, left_index=True, right_index=True).rename(columns={ 'GroupId_y':'GroupId' })
        
        # join both tables with character skill table with the appropriate keys
        char_skill_df = char_skill_df.merge(skill_df, how='left', on='GroupId')
        char_skill_df = char_skill_df.merge(localisation_df, how='left', left_on='LocalizeSkillId', right_on='Key')
        
        return char_skill_df
        
    @functools.cached_property
    def weapon_passive_bonuses(self):
        """Parses UE passive skill bonuses from the localisation table"""
        char_skill_df = self.character_skills
        # select only entries with UE tier 2 get UE passive info
        char_ue_skill_df = char_skill_df[char_skill_df.GroupId.str.contains('WeaponPassive')]#[(char_skill_df['MinimumGradeCharacterWeapon']==2) & (char_skill_df['SkillCategory']=='Passive')]
        # group by passive skill group id and get UE passive bonus
        ue_passive_df = char_ue_skill_df.groupby('CharacterId', sort=False).apply(_parse_ue_passive_stats)
        
        return ue_passive_df
    
    @functools.cached_property
    def character_skill_details(self):
        """Parses most character skills from the localisation table"""
        char_skill_df = self.character_skills
        # select only students and only base skills without UE
        char_skill_df2 = char_skill_df[char_skill_df['MinimumGradeCharacterWeapon']==0]
        # get skill information from description
        char_skill_df2 = char_skill_df2.groupby(['CharacterId', 'GroupId']).apply(_parse_skill_desc)
        # map column names to english
        char_skill_df2.Action = char_skill_df2.Action.map(action_map)
        char_skill_df2.Status = char_skill_df2.Status.map(jp_stat_name_map)
        
        return char_skill_df2
    
    @functools.cached_property
    def currencies(self):
        """Gets the currency table from the repo"""
        # fetch
        curr_df = _get_game_data(self._url_root + "CurrencyExcelTable.json")
        # localisation
        curr_localisation_df = self.combine_localisation("LocalizeEtcExcelTable.json")
        # join
        curr_df = curr_df.merge(curr_localisation_df, how='left', left_on='LocalizeEtcId', right_on='Key')
        curr_df = curr_df.rename(columns={"ID": "Id"})
        
        return curr_df
    
    @functools.cached_property
    def items(self):
        """Gets the item table from the repo"""
        # fetch the items table
        items_df = _get_game_data(self._url_root + "ItemExcelTable.json")
        # fetch the localisation table
        items_localisation_df = self.combine_localisation("LocalizeEtcExcelTable.json")
        # join the localisation table
        items_df = items_df.merge(items_localisation_df, how='left', left_on='LocalizeEtcId', right_on='Key')
        
        return items_df
    
    @functools.cached_property
    def equipment(self):
        """Gets the equipment table from the repo"""
        # fetch tables
        eq_df = _get_game_data(self._url_root + "EquipmentExcelTable.json")
        eq_stats_df = _get_game_data(self._url_root + "EquipmentStatExcelTable.json")
        eq_localisation_df = self.combine_localisation("LocalizeEtcExcelTable.json")
        # join
        eq_df = eq_df.merge(eq_stats_df, how='left', left_on='Id', right_on='EquipmentId', suffixes=[None, '_dupe'])
        eq_df = eq_df.merge(eq_localisation_df, how='left', left_on='LocalizeEtcId', right_on='Key')
        
        return eq_df
    
    @functools.cached_property
    def furnitures(self):
        """Gets the furniture table from the repo"""
        # fetch
        furn_df = _get_game_data(self._url_root + "FurnitureExcelTable.json")
        furn_localisation_df = self.combine_localisation("LocalizeEtcExcelTable.json")
        # join
        furn_df = furn_df.merge(furn_localisation_df, how='left', left_on='LocalizeEtcId', right_on='Key')
        
        return furn_df
    
    @functools.cached_property
    def recipes(self):
        """Gets the recipe table"""
        # fetch tables
        recipe_df = _get_game_data(self._url_root + "RecipeExcelTable.json")
        ingredient_df = _get_game_data(self._url_root + "RecipeIngredientExcelTable.json")
        #join
        recipe_df = recipe_df.merge(ingredient_df, how='left', left_on='RecipeIngredientId', right_on='Id', suffixes=[None, '_dupe'])
        
        return recipe_df
    
    @functools.cached_property
    def student_names(self):
        """Gets student names and their associated IDs from the repo"""
        cd = self.character_details
        students = cd[cd.IsPlayableCharacter & (cd.ProductionStep=='Release')]

        return students[['CharacterId', 'DevName', 'BackupName'] + Localization.all_langs().localize('Name')]
    
    @functools.cached_property
    def character_names(self):
        """Gets all character names with the correct student names"""
        return self.character_details[['CharacterId', 'DevName', 'BackupName'] + Localization.all_langs().localize('Name')]
    
    def list_characters(self, substr='', student_only=True, lang=Localization('en')):
        """Lists all unit names
        
        :param substr: Substring to filter the names by
        :return list: The list of names of all characters with available data, filtered if required.
        """
        names_df = self.student_names if student_only else self.character_names
        
        # check for containing substring
        if substr:
            mask = names_df.filter(like='Name', axis=1).apply(lambda r: r.str.contains(substr, case=False).any(), axis=1)
            names_df = names_df[mask]
        
        return names_df.set_index('CharacterId')[['DevName', 'BackupName'] + lang.localize('Name')].to_dict(orient='index')
    
    def find_character(self, lookup_key=[], lookup_value=[], student_only=True, lang=Localization('en')):
        """Creates a Character object based on the lookup key
        
        :param lookup: Either character name or character id to look up by
        :return BACharacter: Object that holds methods to extract character information
        """
        cd = self.character_details
        details_df = cd[cd.IsPlayableCharacter & (cd.ProductionStep=='Release')] if student_only else cd
        
        selected_ids = []
        if not lookup_key and not lookup_value:
            # return all characters
            selected_ids = details_df.CharacterId.tolist()#[['CharacterId'] + lang.localize('Name')].to_dict(orient='records')
        elif lookup_key:
            # make lookups into lists if not already
            if isinstance(lookup_key, str):
                lookup_key = [lookup_key]
                lookup_value = [lookup_value]

            # filter by magic
            if (lookup_zip := list(filter(lambda k: k[0] in details_df.columns, zip(lookup_key, lookup_value)))):
                lookup_key, lookup_value = zip(*lookup_zip)
            else:
                return []

            # make mask based on filter criteria
            mask = functools.reduce(logical_and, [details_df[k].isin(v) for k,v in zip(lookup_key, lookup_value)])
            selected_ids = details_df[mask].CharacterId.tolist()#[['CharacterId'] + lang.localize('Name')].to_dict(orient='records')
        
        return selected_ids
    
    def _get_generic_asset(self, asset, lookup_key=[], lookup_value=[], keep_cols=None, localize_cols=[], lang=Localization('en'), index='Id'):
        """Gets a generic asset (item, currency, equipment, furniture) by a lookup key"""
        # combine column filters
        if keep_cols is None:
            # keep all by default
            keep_cols = list(asset.columns)
        filter_cols = set((order_cols := keep_cols + lang.localize(*localize_cols)))
        
        if not lookup_key and not lookup_value:
            # return entire asset
            return asset.filter(items=filter_cols)[order_cols].set_index(index).to_dict(orient='index')
        
        # make into lists if not already
        if isinstance(lookup_key, str):
            lookup_key = [lookup_key]
            lookup_value = [lookup_value]
            
        # filter by magic
        if (lookup_zip := list(filter(lambda k: k[0] in asset.columns, zip(lookup_key, lookup_value)))):
            lookup_key, lookup_value = zip(*lookup_zip)
        else:
            return {}
        
        mask = functools.reduce(logical_and, [asset[k].isin(v) for k,v in zip(lookup_key, lookup_value)])
        return asset.filter(items=filter_cols)[mask][order_cols].set_index(index).to_dict(orient='index')
    
    def get_skill(self, lookup_key=[], lookup_value=[], lang=Localization('en')):
        """Gets recipe by ID and looks up parcels involved in it
        
        :param lookup: the ID to look up recipe by
        :param lang: the localisation language to use
        :return dict: dictionary of recipe data
        """
        skills_clean = self.character_skills.drop_duplicates(subset=['GroupId', 'Level'])
        return self._get_generic_asset(skills_clean, lookup_key, lookup_value, skill_keep_keys, ['Name', 'Description'], lang)
    
    def get_recipe(self, lookup_key=[], lookup_value=[], lang=Localization('en')):
        """Gets recipe by ID and looks up parcels involved in it
        
        :param lookup: the ID to look up recipe by
        :param lang: the localisation language to use
        :return dict: dictionary of recipe data
        """
        
        return self._get_generic_asset(self.recipes, lookup_key, lookup_value, recipe_keep_keys, lang=lang)
    
        rcps = self._get_generic_asset(self.recipes, lookup, recipe_keep_keys, lang=lang)
        recipe_list = []
        for recipe in rcps:
            # initialise return dict
            recipe_dict = {
                "Id": recipe['Id'],
                "Type": recipe['RecipeType'],
                "CostTimeInSecond": recipe['CostTimeInSecond'],
            }
            # process the components
            # yield
            recipe_yield = self._get_parcel(recipe['ParcelType'], recipe['ParcelId'], recipe['ResultAmountMax'], lang)
            # add the appropriate keys
            recipe_dict["Yield"] = recipe_yield
            # cost
            if not isinstance(recipe['CostParcelType'], list):
                recipe_dict["Cost"] = {}
            else:
                recipe_cost = self._get_parcel(recipe['CostParcelType'], recipe['CostId'], recipe['CostAmount'], lang)
                recipe_dict["Cost"] = recipe_cost
            # ingredient
            if not isinstance(recipe['IngredientParcelType'], list):
                recipe_dict["Ingredient"] = {}
            else:
                recipe_ingredient = self._get_parcel(recipe['IngredientParcelType'], recipe['IngredientId'], recipe['IngredientAmount'], lang)
                recipe_dict["Ingredient"] = recipe_ingredient
            recipe_list.append(recipe_dict)
        
        return recipe_list
    
    def get_item(self, lookup_key=[], lookup_value=[], lang=Localization('en')):
        """Gets item by ID and returns a dict of its data
        
        :param lookup: the ID to look up item by
        :param lang: the localisation language to use
        :return dict: dictionary of item data
        """
        
        return self._get_generic_asset(self.items, lookup_key, lookup_value, item_keep_keys, ['Name', 'Description'], lang)
    
    def get_currency(self, lookup_key=[], lookup_value=[], lang=Localization('en')):
        """Gets currency by ID and returns a dict of its data
        
        :param lookup: the ID to look up currency by
        :param lang: the localisation language to use
        :return dict: dictionary of currency data
        """
        
        return self._get_generic_asset(self.currencies, lookup_key, lookup_value, currency_keep_keys, ['Name', 'Description'], lang)
    
    def get_equipment(self, lookup_key=[], lookup_value=[], lang=Localization('en')):
        """Gets equipment by ID and returns a dict of its data
        
        :param lookup: the ID to look up equipment by
        :param lang: the localisation language to use
        :return dict: dictionary of equipment data
        """
        
        return self._get_generic_asset(self.equipment, lookup_key, lookup_value, equipment_keep_keys, ['Name', 'Description'], lang)
    
    def get_furniture(self, lookup_key=[], lookup_value=[], lang=Localization('en')):
        """Gets furniture by ID and returns a dict of its data
        
        :param lookup: the ID to look up furniture by
        :param lang: the localisation language to use
        :return dict: dictionary of furniture data
        """
        
        return self._get_generic_asset(self.furnitures, lookup_key, lookup_value, furniture_keep_keys, ['Name', 'Description'], lang)
    

class BACharacter():
    def __init__(self, master, char_id, lang=Localization('en')):
        self._master = master
        self._id = char_id
        self.lang = lang
        self.is_student = (char_id in master.student_names.CharacterId.values)
    
    def summary(self):
        # initialise
        summary_dict = self.basic_info()
        summary_dict['Stats'] = self.stats()
        summary_dict['Details'] = self.details()
        summary_dict['Profile'] = self.profile()
        summary_dict['Skills'] = self.skills()
        summary_dict['SkillDetails'] = self.skill_details()
        summary_dict['Weapon'] = self.weapon()
        summary_dict['WeaponPassive'] = self.weapon_passive()
        summary_dict['BondStats'] = self.bond()
        
        return summary_dict
    
    def basic_info(self):
        return self._master.character_details.set_index('CharacterId').loc[self._id][self.lang.localize('Name') + info_keep_keys].to_dict()
    
    def stats(self):
        return self._master.character_stats.set_index('CharacterId').loc[self._id].to_dict()
    
    def details(self):
        return self._master.character_details.set_index('CharacterId').loc[self._id][details_keep_keys].to_dict()
    
    def skills(self):
        try:
            skill_df = self._master.character_skills.set_index('CharacterId').loc[self._id]
            if isinstance(skill_df, pd.Series):
                skill_df = skill_df.to_frame().transpose()
            skill_df = skill_df.drop_duplicates(subset=['GroupId', 'Level']).set_index(['GroupId', 'Level'])
        except KeyError:
            return {}
        
        skill_dict = {}
        for group,df in skill_df.groupby(level=0):
            group_dict = {
                "MinimumWeaponTier": df.MinimumGradeCharacterWeapon.iloc[0],
                "SkillCategory": df.SkillCategory.iloc[0],
                "Levels": df.loc[group][self.lang.localize('Name', 'Description') + ['RequireLevelUpMaterial']].to_dict(orient='index')
            }
            skill_dict[group] = group_dict
            
        return skill_dict
    
    def skill_details(self):
        # get table
        try:
            skill_details_df = self._master.character_skill_details.loc[self._id]
        except KeyError:
            return {}
        
        # unpack the first level of index (group)
        # then take the df cross section across that level
        # and convert each subgroup individually to dict
        return {group: skill_details_df.xs(group).to_dict('index') for group in skill_details_df.index.remove_unused_levels().levels[0]}
    
    def profile(self):
        if not self.is_student:
            return {}
        elif self.is_student:
            return self._master.character_profiles.set_index('CharacterId')\
                        .loc[self._id][['BirthDay'] + self.lang.localize(*profile_localize_keys)].to_dict()
        
    def weapon(self):
        if not self.is_student:
            return {}
        elif self.is_student:
            # get table
            weapon_df = self._master.character_weapon.set_index('CharacterId').loc[self._id] 
            # fix terrain bonus text
            weapon_df['TerrainBonus'] = adaptation_weapon_map[weapon_df.StatType[2]]

            return weapon_df[weapon_keep_keys].to_dict()
    
    def weapon_passive(self):
        if not self.is_student:
            return {}
        elif self.is_student:
            # get table and convert to dict
            weapon_passive_dict = self._master.weapon_passive_bonuses.loc[self._id].to_dict(orient='list')
            # replace weapon stat name by the first entry
            weapon_passive_dict['WeaponPassiveStatName'] = weapon_passive_dict['WeaponPassiveStatName'][0]
        
            return weapon_passive_dict
    
    def bond(self):
        if not self.is_student:
            return {}
        elif self.is_student:
            # get table
            bond_df = self._master.character_bond_stats.set_index('CharacterId').loc[self._id]
            # index by level and convert to dict 
            bond_dict = bond_df.set_index('Level').to_dict(orient='list')
            # replace stat name lists with first entry
            bond_dict['Stat1'] = bond_dict['Stat1'][0]
            bond_dict['Stat2'] = bond_dict['Stat2'][0]

            return bond_dict

    
if __name__ == "__main__":

    bad = BAData()

    b = BACharacter(bad, 10000, lang=Localization('en', 'jp'))
    
    from app.encoder import NumpyEncoder

    with open('test.json', 'w') as file:
        json.dump(b.summary(), file, indent=4, ensure_ascii=False, cls=NumpyEncoder)


