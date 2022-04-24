# fields to keep in items json
item_keep_keys = ['Id', 'GroupId', 'Rarity', 'ProductionStep', 'ItemCategory',
       'Quality', 'Icon', 'SpriteName', 'StackableMax', 'StackableFunction',
       'ImmediateUse', 'UsingResultParcelType', 'UsingResultId',
       'UsingResultAmount', 'MailType', 'ExpiryChangeParcelType',
       'ExpiryChangeId', 'ExpiryChangeAmount', 'CanTierUpgrade',
       'TierUpgradeRecipeCraftId', 'Tags', 'CraftQuality',
       'ShiftingCraftQuality', 'ShopCategory', 'ExpirationDateTime',
       'ShortcutTypeId', 'GachaTicket']

# fields to keep in currencies json
currency_keep_keys = ['Id', 'CurrencyType', 'Icon', 'Rarity',
       'AutoChargeMsc', 'AutoChargeAmount', 'CurrencyOverChargeType',
       'CurrencyAdditionalChargeType', 'ChargeLimit', 'OverChargeLimit',
       'SpriteName', 'DailyRefillAmount', 'DailyRefillTime']

# fields to keep in equipment json
equipment_keep_keys = ['Id', 'EquipmentCategory', 'Rarity', 'Wear', 'MaxLevel',
       'RecipeId', 'TierInit', 'NextTierEquipment', 'StackableMax', 'Icon',
       'ImageName', 'Tags', 'CraftQuality', 'ShiftingCraftQuality',
       'ShopCategory', 'ShortcutTypeId', 'StatLevelUpType',
       'StatType', 'MinStat', 'MaxStat', 'LevelUpInsertLimit',
       'LevelUpFeedExp', 'LevelUpFeedCostCurrency', 'LevelUpFeedCostAmount',
       'LevelUpFeedAddExp', 'DefaultMaxLevel',
       'TranscendenceMax', 'DamageFactorGroupId']

# fields to keep in furnitures json
furniture_keep_keys = ['Id', 'ProductionStep', 'Rarity', 'Category', 'SubCategory',
       'StarGradeInit', 'Tier', 'Icon', 'SizeWidth',
       'SizeHeight', 'OtherSize', 'ExpandWidth', 'Enable', 'ReverseRotation',
       'Prefab', 'PrefabExpand', 'SubPrefab', 'SubExpandPrefab',
       'CornerPrefab', 'StackableMax', 'RecipeCraftId', 'SetGroudpId',
       'ComfortBonus', 'VisitOperationType', 'VisitBonusOperationType', 'Tags',
       'CraftQuality', 'ShiftingCraftQuality', 'FurnitureFunctionType',
       'FunctionParameter', 'EventCollectionId', 'FurnitureBubbleOffsetX',
       'FurnitureBubbleOffsetY', 'CafeCharacterStateReq',
       'CafeCharacterStateAdd']

# fields to keep in recipes json
recipe_keep_keys = ['Id', 'RecipeType', 'RecipeIngredientId', 'ParcelType', 'ParcelId', 
                    'ResultAmountMin', 'ResultAmountMax', 'CostParcelType', 'CostId',
                    'CostAmount', 'IngredientParcelType','IngredientId',
                    'IngredientAmount', 'CostTimeInSecond']

# fields to keep in skills json
skill_keep_keys = ['GroupId', 'Id', 'MinimumGradeCharacterWeapon', 
                   'SkillCategory', 'Level', 'SkillCost', 'ExtraSkillCost', 
                   'EnemySkillCost', 'ExtraEnemySkillCost', 'BulletType', 'StartCoolTime', 
                   'CoolTime', 'EnemyStartCoolTime', 'EnemyCoolTime', 'UseAtg', 
                   'RequireCharacterLevel', 'RequireLevelUpMaterial', 'IconName', 'IsShowInfo']

# fix some of the names from extracting unknown names with a hacky method
name_fix = {
    "Tusbaki": "Tsubaki",
    "Zunko": "Junko",
    "Hihumi": "Hifumi",
    "Hihumi_Swimsuit": "Hifumi_Swimsuit"
}

# fix damage type names
damage_type_map = {
    "Explosion": "Explosive",
    "Pierce": "Piercing",
    "Mystic": "Mystic",
    "Siege": "Siege",
    "Normal": "Normal"
}

# fix armour type names
armour_type_map = {
    "LightArmor": "Light",
    "HeavyArmor": "Heavy",
    "Unarmed": "Special"
}

# fix skill group names
skill_category_map = {
    "ExSkillGroupId": "Ex",
    "PublicSkillGroupId": "Normal",
    "PassiveSkillGroupId": "Passive",
    "ExtraPassiveSkillGroupId": "Sub"
}

# multipliers for mood ranks
adaptation_multiplier_map = {
    'S': 1.2,
    'A': 1.1,
    'B': 1.0,
    'C': 0.9,
    'D': 0.8
}

# parsing UE terrain bonus type
adaptation_weapon_map = {
    'StreetBattleAdaptation_Base': 'Urban',
    'OutdoorBattleAdaptation_Base': 'Outdoor',
    'IndoorBattleAdaptation_Base': 'Indoor'
}

# parsing bond stat type 
bond_stat_type_map = {
    'AttackPower_Base': 'Attack',
    'DefensePower_Base': 'Defence',
    'HealPower_Base': 'Heal',
    'MaxHP_Base': 'Hp'
}

# dictionary to rename all the stat fields to something sensible
character_stats_column_map = {
    'StabilityPoint': 'Stability',
    'DodgePoint': 'Evasion',
    'AccuracyPoint': 'Accuracy',
    'CriticalPoint': 'Crit',
    'CriticalResistPoint': 'CritRes',
    'CriticalDamageRate': 'CritDmg',
    'CriticalDamageResistRate': 'CritDmgRes',
    'BlockRate': 'BlockRate',
    'HealEffectivenessRate': 'Recovery',
    'OppressionPower': 'CCStrength',
    'OppressionResist': 'CCRes',
    'StreetBattleAdaptation': 'UrbanAffinity',
    'OutdoorBattleAdaptation': 'OutdoorAffinity',
    'IndoorBattleAdaptation': 'IndoorAffinity',
}

# parsing stats used in JP skill descriptions
jp_stat_name_map = {
    '会心ダメージ': "CritDmg",
    '会心ダメージ率': "CritDmg",
    '被回復値': "Recovery",
    '被回復率': "Recovery",
    'HP': "Hp",
    '攻撃力': "Attack",
    '通常攻撃': "Attack", # hacky key to make Shun's EX work
    '防御力': "Defense",
    '命中値': "Accuracy",
    '攻撃速度': "NormalAttackSpeed", 
    '会心値': "Crit",
    '装弾数': "AmmoCount",
    'CC強化力': "CCStrength", 
    '防御貫通値': "DefensePenetration", 
    '回避値': "Evasion",
    '遮蔽成功値': "BlockRate",
    '安定値': "Stability",
    '治癒力': "Heal",
    'コスト回復力': "RegenCost",
    '射程': "Range",
    '移動速度': "MoveSpeed",
    '会心抵抗値': "CritRes",
    '会心ダメージ抵抗率': "CritDmgRes",
    'CC強化力': "CCStrength",
    'CC抵抗力': "CCRes",
    '被ダメージ量': "DamagedRatio",
    '受けるダメージ量': "DamagedRatio"
}

# parsing skill actions
action_map = {
    'ダメージ': "Damage",
    '回復': "Heal",
    'シールド': "Shield",
    '持ち': "Summon",
    '増加': "Buff",
    '減少': "Debuff"
}

# fields to keep for individual character data
# basic details
basic_keep_keys = ['DevName', 'ProductionStep', 'IsPlayableCharacter',
                   'Rarity', 'TacticRole', 'TacticRange', 'WeaponType',
                   'BulletType', 'ArmorType', 'School', 'Club',
                   'DefaultStarGrade', 'MaxStarGrade', 'SquadType', 
                   'EquipmentSlot', 'Tags']

# extra details
details_keep_keys = ['CollectionVisible', 'TacticEntityType', 'CanSurvive', 'IsDummy',
                     'SubPartsCount', 'AimIKType', 'StatLevelUpType', 'Jumpable', 
                     'PersonalityId', 'CharacterAIId', 'ScenarioCharacter',
                     'SpawnTemplateId', 'FavorLevelupType', 'SpineResourceName', 
                     'SpineResourceNameDiorama', 'EntityMaterialType', 'ModelPrefabName', 
                     'TextureDir', 'TextureEchelon', 'CollectionTexturePath', 
                     'CollectionBGTexturePath', 'TextureBoss', 'TextureSkillCard', 
                     'WeaponImagePath', 'WeaponLocalizeId', 'DisplayEnemyInfo', 
                     'BodyRadius', 'RandomEffectRadius', 'HPBarHide', 'HpBarHeight', 
                     'HighlightFloaterHeight', 'MoveStartFrame', 'MoveEndFrame', 
                     'JumpMotionFrame', 'AppearFrame', 'CanMove', 'CanFix', 
                     'CanCrowdControl', 'CanBattleItemMove', 'IsAirUnit', 'AirUnitHeight', 
                     'SecretStoneItemId', 'SecretStoneItemAmount', 'CharacterPieceItemId', 
                     'CharacterPieceItemAmount', 'CombineRecipeId', 'InformationPacel', 
                     'AnimationSSR']

# UE details
weapon_keep_keys = ['AttackPower', 'AttackPower100', 
                    'MaxHP', 'MaxHP100', 'HealPower', 'HealPower100',
                    'TerrainBonus', 'Unlock', 'MaxLevel', 'RecipeId', 'ImagePath']

# fields that need be localised in character profiles
profile_localize_keys = ['StatusMessage', 'FullName', 'FamilyName', 'FamilyNameRuby', 
                     'PersonalName', 'PersonalNameRuby', 'SchoolYear', 'CharacterAge', 
                     'Birthday', 'CharHeight', 'ArtistName', 'CharacterVoice', 'Hobby', 
                     'WeaponName', 'WeaponDesc', 'ProfileIntroduction', 'CharacterSSRNew'] 

