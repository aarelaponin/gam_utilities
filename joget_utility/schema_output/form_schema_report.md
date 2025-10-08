# Form Database Schema Report

Total Forms: 11

## Form: 01.05-1 - Crop Management Form
- **Form ID:** `cropManagementForm`
- **Table Name:** `crop_management`
- **Primary Key:** `id`
- **Total Fields:** 7

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| farmer_id | c_farmer_id | HiddenField |  | No |
| cropType | c_cropType | SelectBox | Crop Type | No |
| areaCultivated | c_areaCultivated | TextField | Area Cultivated | No |
| areaUnit | c_areaUnit | SelectBox | Area Unit | No |
| bagsHarvested | c_bagsHarvested | TextField | 50kg Bags Harvested | No |
| fertilizerApplied | c_fertilizerApplied | SelectBox | Did you apply fertilizer? | No |
| pesticidesApplied | c_pesticidesApplied | SelectBox | Did you apply pesticides/herbicides? | No |

---

## Form: 01.03 - Farmer Agricultural Activities
- **Form ID:** `farmerAgriculture`
- **Table Name:** `farmer_registry`
- **Primary Key:** `id`
- **Total Fields:** 14

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| agriculture_key | c_agriculture_key | HiddenField |  | No |
| cropProduction | c_cropProduction | Radio | Was the household engaged in crop production last agricultural season? | No |
| livestockProduction | c_livestockProduction | Radio | Was the household engaged in livestock production last agricultural season? | No |
| canReadWrite | c_canReadWrite | Radio | Can the head read and write? | No |
| parent_id | c_parent_id | HiddenField |  | No |
| mainSourceFarmLabour | c_mainSourceFarmLabour | SelectBox | What is your main source of farm labour? | No |
| mainSourceLivelihood | c_mainSourceLivelihood | SelectBox | What is your main source of livelihood? | No |
| agriculturalManagementSkills | c_agriculturalManagementSkills | SelectBox | What is the level of agricultural management skills? | No |
| mainSourceAgriculturalInfo | c_mainSourceAgriculturalInfo | SelectBox | What is your main source of agricultural information? | No |
| conservationPractices | c_conservationPractices | SelectBox | Agriculture Conservation Practices | No |
| conservationPracticesOther | c_conservationPracticesOther | TextField | Other Conservation Practices (Specify) | No |
| shocks_hazards | c_shocks_hazards | SelectBox | Shocks/hazards | No |
| otherHazards | c_otherHazards | TextField | Other Hazards (Specify) | No |
| copingMechanisms | c_copingMechanisms | TextArea | What did the household do to cope with any of these shocks/hazards? | No |

---

## Form: 01.01 - Farmer Basic Information
- **Form ID:** `farmerBasicInfo`
- **Table Name:** `farmer_basic_data`
- **Primary Key:** `id`
- **Total Fields:** 13

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| national_id | c_national_id | TextField | National ID | No |
| first_name | c_first_name | TextField | First Name | No |
| last_name | c_last_name | TextField | Last Name | No |
| gender | c_gender | Radio | Gender | No |
| date_of_birth | c_date_of_birth | DatePicker | Date of Birth | No |
| marital_status | c_marital_status | SelectBox | Marital Status | No |
| preferred_language | c_preferred_language | SelectBox | Preferred Language | No |
| mobile_number | c_mobile_number | TextField | Mobile Number | No |
| email_address | c_email_address | TextField | Email Address | No |
| extension_officer_name | c_extension_officer_name | TextField | Extension Officer Name | No |
| member_of_cooperative | c_member_of_cooperative | Radio | Cooperative member? | No |
| cooperative_name | c_cooperative_name | TextField | Cooperative Name | No |
| parent_id | c_parent_id | HiddenField |  | No |

---

## Form: 01.05 - Farmer Crops and Livestock
- **Form ID:** `farmerCropsLivestock`
- **Table Name:** `farmer_crop_livestck`
- **Primary Key:** `id`
- **Total Fields:** 6

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| parent_id | c_parent_id | HiddenField |  | No |
| crops_livestock_key | c_crops_livestock_key | HiddenField |  | No |
| cropInstruction | c_cropInstruction | CustomHTML |  | No |
| **cropManagement** (Grid) | - | Grid | Crop Management | - |
| hasLivestock | c_hasLivestock | Radio | Do you have livestock? | No |
| **livestockDetails** (Grid) | - | Grid | Livestock Details | - |

---

## Form: 01.07 - Farmer Declaration
- **Form ID:** `farmerDeclaration`
- **Table Name:** `farmer_declaration`
- **Primary Key:** `id`
- **Total Fields:** 13

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| parent_id | c_parent_id | HiddenField |  | No |
| declaration_key | c_declaration_key | HiddenField |  | No |
| declarationHeader | c_declarationHeader | CustomHTML |  | No |
| declarationText | c_declarationText | CustomHTML |  | No |
| declarationConsent | c_declarationConsent | CheckBox |  | No |
| declarationFullName | c_declarationFullName | TextField | Full Name (as per National ID) | No |
| field13 | c_field13 | DatePicker | Date Picker | No |
| field12 | c_field12 | Signature | Signature | No |
| registrationInfo | c_registrationInfo | CustomHTML |  | No |
| registrationStation | c_registrationStation | TextField | Registration Station | No |
| beneficiaryCode | c_beneficiaryCode | IdGeneratorField | Beneficiary Code | No |
| registrationChannel | c_registrationChannel | SelectBox | Registration Channel | No |
| registrationStatus | c_registrationStatus | HiddenField |  | No |

---

## Form: 01.04 - Farmer Household Members
- **Form ID:** `farmerHousehold`
- **Table Name:** `farmer_registry`
- **Primary Key:** `id`
- **Total Fields:** 4

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| household_key | c_household_key | HiddenField |  | No |
| parent_id | c_parent_id | HiddenField |  | No |
| householdInstruction | c_householdInstruction | CustomHTML |  | No |
| **householdMembers** (Grid) | - | Grid | Household Members | - |

---

## Form: 01.06 - Farmer Income and Programs
- **Form ID:** `farmerIncomePrograms`
- **Table Name:** `farmer_income`
- **Primary Key:** `id`
- **Total Fields:** 21

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| income_programs_key | c_income_programs_key | HiddenField |  | No |
| mainSourceIncome | c_mainSourceIncome | SelectBox | Main source of income for the household? | No |
| income_sources | c_income_sources | SelectBox | Income sources (last 12 months) | No |
| gainfulEmployment | c_gainfulEmployment | Radio | Are you in gainful employment where a monthly salary is earned? | No |
| governmentEmployed | c_governmentEmployed | Radio | If yes, are you employed by the Government of Lesotho? | No |
| parent_id | c_parent_id | HiddenField |  | No |
| averageAnnualIncome | c_averageAnnualIncome | TextField | Average annual household income? | No |
| monthlyExpenditure | c_monthlyExpenditure | TextField | Monthly household expenditure? | No |
| relativeSupport | c_relativeSupport | Radio | Receive any support from relative(s) that you rely on entirely for your survival? | No |
| supportFrequency | c_supportFrequency | Radio | Frequency of Support | No |
| supportType | c_supportType | CheckBox | Type of support | No |
| supportProgram | c_supportProgram | SelectBox | Household benefits from support program (last 12 months)? | No |
| creditDefault | c_creditDefault | Radio | Is any member of the household in default of any agriculture credit scheme? | No |
| everOnISP | c_everOnISP | Radio | Has any member of the household ever been on ISP? | No |
| otherInputSupport | c_otherInputSupport | Radio | Has any member of the household ever been on Other Input Support program? | No |
| totalLoans12Months | c_totalLoans12Months | TextField | Total amount of loan(s) received in the last 12 months? | No |
| informalTransfers | c_informalTransfers | TextField | Total amount of informal transfers received (cash, remittances, food, seed gift, etc.)? | No |
| networksSupport | c_networksSupport | TextField | Networks Support | No |
| formalTransfers | c_formalTransfers | TextField | Total amount of formal transfers received (relief food, cash assistance, livestock, pensions, etc)? | No |
| networkAssociations | c_networkAssociations | TextField | Associations (farmer groups, cooperatives, women groups, etc.) | No |
| networkRelatives | c_networkRelatives | TextField | Relatives/friends/Family members | No |

---

## Form: 01.02 - Farmer Location and Farm
- **Form ID:** `farmerLocation`
- **Table Name:** `farm_location`
- **Primary Key:** `id`
- **Total Fields:** 20

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| district | c_district | SelectBox | District | No |
| village | c_village | TextField | Village Name | No |
| communityCouncil | c_communityCouncil | TextField | Community Council | No |
| agroEcologicalZone | c_agroEcologicalZone | SelectBox | Agro-Ecological Zone | No |
| residency_type | c_residency_type | SelectBox | Residency Type | No |
| yearsInArea | c_yearsInArea | TextField | Years lived in this area | No |
| gpsLatitude | c_gpsLatitude | TextField | GPS Latitude | No |
| gpsLongitude | c_gpsLongitude | TextField | GPS Longitude | No |
| ownedRentedLand | c_ownedRentedLand | TextField | Owned/Rented Land (Hectares) | No |
| totalAvailableLand | c_totalAvailableLand | TextField | Total Available Land (Hectares) | No |
| cultivatedLand | c_cultivatedLand | TextField | Cultivated Land (Hectares) | No |
| conservationAgricultureLand | c_conservationAgricultureLand | TextField | Land under Conservation Agriculture (Hectares) | No |
| access_to_services | c_access_to_services | TextField | Closest Service | No |
| distanceWaterSource | c_distanceWaterSource | TextField | Water Source | No |
| distancePrimarySchool | c_distancePrimarySchool | TextField | Primary School | No |
| distancePublicHospital | c_distancePublicHospital | TextField | Public Hospital | No |
| distanceLivestockMarket | c_distanceLivestockMarket | TextField | Livestock Market | No |
| distanceAgriculturalMarket | c_distanceAgriculturalMarket | TextField | Agricultural/Crops Market | No |
| distancePublicTransport | c_distancePublicTransport | TextField | Public Means of Transport | No |
| parent_id | c_parent_id | HiddenField |  | No |

---

## Form: 01 - Farmer Registration Form
- **Form ID:** `farmerRegistrationForm`
- **Table Name:** `farms_registry`
- **Primary Key:** `id`
- **Total Fields:** 1

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| farmerRegistrationWizard | c_farmerRegistrationWizard | MultiPagedForm |  | No |

---

## Form: 01.04-1 - Household Member Form
- **Form ID:** `householdMemberForm`
- **Table Name:** `household_members`
- **Primary Key:** `id`
- **Total Fields:** 9

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| farmer_id | c_farmer_id | HiddenField |  | No |
| memberName | c_memberName | TextField | Name (Surname First) | No |
| sex | c_sex | SelectBox | Sex | No |
| date_of_birth | c_date_of_birth | DatePicker | Date of Birth | No |
| relationship | c_relationship | SelectBox | Relationship to Head | No |
| orphanhoodStatus | c_orphanhoodStatus | SelectBox | Orphanhood Status | No |
| participatesInAgriculture | c_participatesInAgriculture | SelectBox | Participates in Agricultural Activities | No |
| disability | c_disability | SelectBox | Disability Status | No |
| chronicallyIll | c_chronicallyIll | SelectBox | Chronically Ill on Palliative Care | No |

---

## Form: 01.05-2 - Livestock Details Form
- **Form ID:** `livestockDetailsForm`
- **Table Name:** `livestock_details`
- **Primary Key:** `id`
- **Total Fields:** 4

### Fields:
| Field ID | Column Name | Type | Label | Required |
|----------|-------------|------|-------|----------|
| farmer_id | c_farmer_id | HiddenField |  | No |
| livestockType | c_livestockType | SelectBox | Livestock Type | No |
| numberOfMale | c_numberOfMale | TextField | Number (Male) | No |
| numberOfFemale | c_numberOfFemale | TextField | Number (Female) | No |

---
