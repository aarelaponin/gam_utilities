# Database Schema Inspection Report

**Database:** `jwdb`
**Inspected:** 2025-09-25T00:29:31.356983
**Total Tables Found:** 40

## Tables Summary

| Table Name | Columns | Primary Key | Row Count |
|------------|---------|-------------|-----------|
| `app_fd_bo_farmer_experience` | 9 | `id` | 2 |
| `app_fd_bo_farmer_reg` | 37 | `id` | 1 |
| `app_fd_crop_management` | 15 | `id` | 3 |
| `app_fd_crops` | 9 | `id` | 21 |
| `app_fd_farm_form` | 18 | `id` | 2 |
| `app_fd_farm_labour_source` | 9 | `id` | 5 |
| `app_fd_farm_land_registry` | 14 | `id` | 2 |
| `app_fd_farm_location` | 28 | `id` | 1 |
| `app_fd_farmer` | 44 | `id` | 0 |
| `app_fd_farmerRegistrationForm` | 10 | `id` | 1 |
| `app_fd_farmer_basic_data` | 21 | `id` | 1 |
| `app_fd_farmer_crop_livestck` | 11 | `id` | 0 |
| `app_fd_farmer_declaration` | 17 | `id` | 0 |
| `app_fd_farmer_experience` | 9 | `id` | 2 |
| `app_fd_farmer_income` | 30 | `id` | 0 |
| `app_fd_farmer_reg_approval` | 12 | `id` | 13 |
| `app_fd_farmer_reg_decision` | 10 | `id` | 0 |
| `app_fd_farmer_reg_record` | 34 | `id` | 0 |
| `app_fd_farmer_reg_review` | 12 | `id` | 1 |
| `app_fd_farmer_registration` | 32 | `id` | 0 |
| `app_fd_farmer_registry` | 52 | `id` | 1 |
| `app_fd_farming_experience` | 8 | `id` | 2 |
| `app_fd_farmland` | 17 | `id` | 0 |
| `app_fd_farmland_usage` | 14 | `id` | 0 |
| `app_fd_farms_registry` | 83 | `id` | 1 |
| `app_fd_fo_farmer_reg` | 30 | `id` | 1 |
| `app_fd_fo_household_reg` | 33 | `id` | 1 |
| `app_fd_household_members` | 17 | `id` | 3 |
| `app_fd_household_reg` | 33 | `id` | 1 |
| `app_fd_income_source` | 9 | `id` | 10 |
| `app_fd_livestock_details` | 12 | `id` | 0 |
| `app_fd_livestock_type` | 9 | `id` | 18 |
| `app_fd_moa_bo_farmer_reg` | 32 | `id` | 2 |
| `app_fd_moa_farmer_reg` | 32 | `id` | 1 |
| `app_fd_reg_farm_form` | 18 | `id` | 0 |
| `app_fd_reg_farm_land_reg` | 14 | `id` | 0 |
| `app_fd_reg_farmer_reg` | 32 | `id` | 0 |
| `app_fd_registry_inspection` | 59 | `id` | 0 |
| `app_fd_sample_farm_land` | 17 | `id` | 1 |
| `app_fd_sample_farmer_form` | 19 | `id` | 1 |

## Detailed Table Structures


### Table: `app_fd_bo_farmer_experience`

- **Row Count:** 2
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_code` | longtext | YES | - | NULL | - |
| `c_name` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "ba59cd22-e968-4c62-9b6f-a1044fd29029",
  "dateCreated": "2025-04-03 17:17:35",
  "dateModified": "2025-04-15 05:04:35",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_code": "E02",
  "c_name": "Hobby"
}
```

---

### Table: `app_fd_bo_farmer_reg`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_residence_proof` | longtext | YES | - | NULL | - |
| `c_elevation` | longtext | YES | - | NULL | - |
| `c_id_scan` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_latitude` | longtext | YES | - | NULL | - |
| `c_primary_language` | longtext | YES | - | NULL | - |
| `c_ward` | longtext | YES | - | NULL | - |
| `c_location_description` | longtext | YES | - | NULL | - |
| `c_primary_phone` | longtext | YES | - | NULL | - |
| `c_passport_photo` | longtext | YES | - | NULL | - |
| `c_vilage` | longtext | YES | - | NULL | - |
| `c_marital_status` | longtext | YES | - | NULL | - |
| `c_full_name` | longtext | YES | - | NULL | - |
| `c_secondary_phone` | longtext | YES | - | NULL | - |
| `c_gps_accuracy` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_farming_experience` | longtext | YES | - | NULL | - |
| `c_email` | longtext | YES | - | NULL | - |
| `c_document_type` | longtext | YES | - | NULL | - |
| `c_upload_date` | longtext | YES | - | NULL | - |
| `c_longitude` | longtext | YES | - | NULL | - |
| `c_dob` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | - | NULL | - |
| `c_application_id` | longtext | YES | - | NULL | - |
| `c_application_number` | longtext | YES | - | NULL | - |
| `c_approval2_id` | longtext | YES | - | NULL | - |
| `c_approval1_id` | longtext | YES | - | NULL | - |
| `c_status` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "337612fa-8fe5-4b75-8c4c-fd3939d2d74c",
  "dateCreated": "2025-07-07 14:47:01",
  "dateModified": "2025-07-07 14:47:34",
  "createdBy": "roleSystem",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_national_id": "111",
  "c_residence_proof": "",
  "c_elevation": "",
  "c_id_scan": "",
  "c_gender": "male",
  "c_date_of_birth": null,
  "c_latitude": "",
  "c_primary_language": "",
  "c_ward": "",
  "c_location_description": "",
  "c_primary_phone": "",
  "c_passport_photo": "",
  "c_vilage": "",
  "c_marital_status": "married_civil",
  "c_full_name": "Peeter Meeter",
  "c_secondary_phone": "",
  "c_gps_accuracy": "",
  "c_district": "D01",
  "c_farming_experience": "",
  "c_email": "",
  "c_document_type": "form_c",
  "c_upload_date": "",
  "c_longitude": "",
  "c_dob": "",
  "c_village": "",
  "c_application_id": "444f6f8c-6aa9-46e2-a91e-f04f908275c7",
  "c_application_number": "AP-000061",
  "c_approval2_id": "",
  "c_approval1_id": "",
  "c_status": "approved"
}
```

---

### Table: `app_fd_crop_management`

- **Row Count:** 3
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_areaUnit` | longtext | YES | - | NULL | - |
| `c_farmer_id` | longtext | YES | - | NULL | - |
| `c_pesticidesApplied` | longtext | YES | - | NULL | - |
| `c_fertilizerApplied` | longtext | YES | - | NULL | - |
| `c_cropType` | longtext | YES | - | NULL | - |
| `c_areaCultivated` | longtext | YES | - | NULL | - |
| `c_bagsHarvested` | longtext | YES | - | NULL | - |
| `c_parentId` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "20227d4e-8e0e-4636-a630-eb5cddf2da88",
  "dateCreated": "2025-09-22 18:30:38",
  "dateModified": "2025-09-22 18:30:38",
  "createdBy": "roleSystem",
  "createdByName": null,
  "modifiedBy": "roleSystem",
  "modifiedByName": null,
  "c_areaUnit": "hectare",
  "c_farmer_id": "farmer-002",
  "c_pesticidesApplied": "no",
  "c_fertilizerApplied": "yes",
  "c_cropType": null,
  "c_areaCultivated": null,
  "c_bagsHarvested": null,
  "c_parentId": null
}
```

---

### Table: `app_fd_crops`

- **Row Count:** 21
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_code` | longtext | YES | - | NULL | - |
| `c_name` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "03815ef9-1421-4b30-8557-60135cdd85b9",
  "dateCreated": "2025-09-21 17:31:49",
  "dateModified": "2025-09-21 17:31:49",
  "createdBy": "roleAnonymous",
  "createdByName": null,
  "modifiedBy": "roleAnonymous",
  "modifiedByName": null,
  "c_code": "wheat",
  "c_name": "Wheat"
}
```

---

### Table: `app_fd_farm_form`

- **Row Count:** 2
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_plot_number` | longtext | YES | - | NULL | - |
| `c_survey_reference_number` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | MUL | NULL | - |
| `c_land_use_type` | longtext | YES | MUL | NULL | - |
| `c_calculated_area` | longtext | YES | - | NULL | - |
| `c_survey_date` | longtext | YES | - | NULL | - |
| `c_spatial_data_files` | longtext | YES | - | NULL | - |
| `c_surveyor_name` | longtext | YES | - | NULL | - |
| `c_plot_boundary` | longtext | YES | - | NULL | - |
| `c_ownership_status` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | MUL | NULL | - |

#### Sample Data:

```json
{
  "id": "7e76847c-def3-4156-9dc0-66bedf076cb8",
  "dateCreated": "2024-12-19 11:14:45",
  "dateModified": "2024-12-19 11:14:45",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_plot_number": "1111",
  "c_survey_reference_number": "ID-000003",
  "c_district": "9315e12f-9459-4bf3-9ee0-2471c56fee72",
  "c_land_use_type": "",
  "c_calculated_area": "",
  "c_survey_date": "",
  "c_spatial_data_files": "",
  "c_surveyor_name": "",
  "c_plot_boundary": "farmland-geojson.json",
  "c_ownership_status": "owned",
  "c_village": "0a552ada-5ab3-408f-bad8-8a1af8180fa9"
}
```

---

### Table: `app_fd_farm_labour_source`

- **Row Count:** 5
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_code` | longtext | YES | - | NULL | - |
| `c_name` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "084b87df-0480-4b73-b782-81b3e1cd7dc7",
  "dateCreated": "2025-09-21 17:31:23",
  "dateModified": "2025-09-21 17:31:23",
  "createdBy": "roleAnonymous",
  "createdByName": null,
  "modifiedBy": "roleAnonymous",
  "modifiedByName": null,
  "c_code": "mixed",
  "c_name": "Mixed"
}
```

---

### Table: `app_fd_farm_land_registry`

- **Row Count:** 2
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_end_date` | longtext | YES | - | NULL | - |
| `c_additional_notes` | longtext | YES | - | NULL | - |
| `c_supporting_documents` | longtext | YES | - | NULL | - |
| `c_farmer` | longtext | YES | MUL | NULL | - |
| `c_type_of_right` | longtext | YES | - | NULL | - |
| `c_farmland` | longtext | YES | MUL | NULL | - |
| `c_start_date` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "36b20bdb-064b-4635-aa41-6bddde9712f9",
  "dateCreated": "2024-12-17 23:12:37",
  "dateModified": "2024-12-18 11:13:16",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_end_date": "",
  "c_additional_notes": "",
  "c_supporting_documents": "",
  "c_farmer": "a38641b7-f080-4d85-9a11-f6fb1671c62a",
  "c_type_of_right": "customary",
  "c_farmland": "d1c5b71c-2e2b-4c33-980d-1c09b7b7523f",
  "c_start_date": "2024-12-02"
}
```

---

### Table: `app_fd_farm_location`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_conservationAgricultureLand` | longtext | YES | - | NULL | - |
| `c_communityCouncil` | longtext | YES | - | NULL | - |
| `c_gpsLongitude` | longtext | YES | - | NULL | - |
| `c_distanceAgriculturalMarket` | longtext | YES | - | NULL | - |
| `c_cultivatedLand` | longtext | YES | - | NULL | - |
| `c_distanceWaterSource` | longtext | YES | - | NULL | - |
| `c_ownedRentedLand` | longtext | YES | - | NULL | - |
| `c_access_to_services` | longtext | YES | - | NULL | - |
| `c_residency_type` | longtext | YES | - | NULL | - |
| `c_agroEcologicalZone` | longtext | YES | - | NULL | - |
| `c_distanceLivestockMarket` | longtext | YES | - | NULL | - |
| `c_parent_id` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_distancePrimarySchool` | longtext | YES | - | NULL | - |
| `c_yearsInArea` | longtext | YES | - | NULL | - |
| `c_distancePublicTransport` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | - | NULL | - |
| `c_distancePublicHospital` | longtext | YES | - | NULL | - |
| `c_totalAvailableLand` | longtext | YES | - | NULL | - |
| `c_gpsLatitude` | longtext | YES | - | NULL | - |
| `c_residency` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "farmer-002",
  "dateCreated": "2025-09-22 18:30:38",
  "dateModified": "2025-09-22 18:30:38",
  "createdBy": "roleSystem",
  "createdByName": null,
  "modifiedBy": "roleSystem",
  "modifiedByName": null,
  "c_conservationAgricultureLand": null,
  "c_communityCouncil": "Machache Community Council",
  "c_gpsLongitude": null,
  "c_distanceAgriculturalMarket": null,
  "c_cultivatedLand": null,
  "c_distanceWaterSource": null,
  "c_ownedRentedLand": null,
  "c_access_to_services": null,
  "c_residency_type": null,
  "c_agroEcologicalZone": null,
  "c_distanceLivestockMarket": null,
  "c_parent_id": "farmer-002",
  "c_district": "berea",
  "c_distancePrimarySchool": null,
  "c_yearsInArea": null,
  "c_distancePublicTransport": null,
  "c_village": "Ha Nkau",
  "c_distancePublicHospital": null,
  "c_totalAvailableLand": null,
  "c_gpsLatitude": null,
  "c_residency": null
}
```

---

### Table: `app_fd_farmer`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_firstName` | longtext | YES | - | NULL | - |
| `c_primaryPhone` | longtext | YES | - | NULL | - |
| `c_postalAddress` | longtext | YES | - | NULL | - |
| `c_occupation` | longtext | YES | - | NULL | - |
| `c_nationalId` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_surname` | longtext | YES | - | NULL | - |
| `c_middleName` | longtext | YES | - | NULL | - |
| `c_dateOfBirth` | longtext | YES | - | NULL | - |
| `c_yearsExperience` | longtext | YES | - | NULL | - |
| `c_secondaryPhone` | longtext | YES | - | NULL | - |
| `c_email` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_residence_proof` | longtext | YES | - | NULL | - |
| `c_elevation` | longtext | YES | - | NULL | - |
| `c_id_scan` | longtext | YES | - | NULL | - |
| `c_latitude` | longtext | YES | - | NULL | - |
| `c_primary_language` | longtext | YES | - | NULL | - |
| `c_ward` | longtext | YES | - | NULL | - |
| `c_location_description` | longtext | YES | - | NULL | - |
| `c_primary_phone` | longtext | YES | - | NULL | - |
| `c_passport_photo` | longtext | YES | - | NULL | - |
| `c_vilage` | longtext | YES | - | NULL | - |
| `c_marital_status` | longtext | YES | - | NULL | - |
| `c_full_name` | longtext | YES | - | NULL | - |
| `c_secondary_phone` | longtext | YES | - | NULL | - |
| `c_gps_accuracy` | longtext | YES | - | NULL | - |
| `c_dob` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_farming_experience` | longtext | YES | - | NULL | - |
| `c_document_type` | longtext | YES | - | NULL | - |
| `c_upload_date` | longtext | YES | - | NULL | - |
| `c_longitude` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | - | NULL | - |
| `c_application_id` | longtext | YES | - | NULL | - |
| `c_application_number` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_farmerRegistrationForm`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_processId` | longtext | YES | - | NULL | - |
| `c_applicationId` | longtext | YES | - | NULL | - |
| `c_status` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "e81be70b-1b7c-4348-bcb3-2c64471e4ca4",
  "dateCreated": null,
  "dateModified": null,
  "createdBy": null,
  "createdByName": null,
  "modifiedBy": null,
  "modifiedByName": null,
  "c_processId": "9730_formsForAgriEcosystem_farmerApplicationProcess",
  "c_applicationId": "dbc2e50d-31a7-44ca-b6ed-cf0e301d8e53",
  "c_status": "pending"
}
```

---

### Table: `app_fd_farmer_basic_data`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_last_name` | longtext | YES | - | NULL | - |
| `c_extension_officer_name` | longtext | YES | - | NULL | - |
| `c_cooperative_name` | longtext | YES | - | NULL | - |
| `c_marital_status` | longtext | YES | - | NULL | - |
| `c_email_address` | longtext | YES | - | NULL | - |
| `c_parent_id` | longtext | YES | - | NULL | - |
| `c_field9` | longtext | YES | - | NULL | - |
| `c_member_of_cooperative` | longtext | YES | - | NULL | - |
| `c_mobile_number` | longtext | YES | - | NULL | - |
| `c_first_name` | longtext | YES | - | NULL | - |
| `c_preferred_language` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "farmer-002",
  "dateCreated": "2025-09-22 18:30:38",
  "dateModified": "2025-09-24 23:27:56",
  "createdBy": "roleSystem",
  "createdByName": null,
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_national_id": "8712248901234",
  "c_date_of_birth": "1987-12-24",
  "c_last_name": "Motlomelo",
  "c_extension_officer_name": "Sarah Mofokeng",
  "c_cooperative_name": "",
  "c_marital_status": "single",
  "c_email_address": "mamosa.motlomelo@gmail.com",
  "c_parent_id": "farmer-002",
  "c_field9": null,
  "c_member_of_cooperative": "no",
  "c_mobile_number": "+26659876543",
  "c_first_name": "Mamosa",
  "c_preferred_language": "sesotho",
  "c_gender": "female"
}
```

---

### Table: `app_fd_farmer_crop_livestck`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_hasLivestock` | longtext | YES | - | NULL | - |
| `c_parent_id` | longtext | YES | - | NULL | - |
| `c_livestockDetails` | longtext | YES | - | NULL | - |
| `c_crops_livestock_key` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_farmer_declaration`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_field12` | longtext | YES | - | NULL | - |
| `c_declaration_key` | longtext | YES | - | NULL | - |
| `c_registrationStatus` | longtext | YES | - | NULL | - |
| `c_beneficiaryCode` | longtext | YES | - | NULL | - |
| `c_parent_id` | longtext | YES | - | NULL | - |
| `c_field13` | longtext | YES | - | NULL | - |
| `c_declarationFullName` | longtext | YES | - | NULL | - |
| `c_declarationConsent` | longtext | YES | - | NULL | - |
| `c_registrationStation` | longtext | YES | - | NULL | - |
| `c_registrationChannel` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_farmer_experience`

- **Row Count:** 2
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_code` | longtext | YES | - | NULL | - |
| `c_name` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "7d7bc64a-04b6-44b7-9d1c-b7244c91caa5",
  "dateCreated": "2025-03-29 21:28:47",
  "dateModified": "2025-03-29 21:28:47",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_code": "E01",
  "c_name": "Experienced"
}
```

---

### Table: `app_fd_farmer_income`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_supportType` | longtext | YES | - | NULL | - |
| `c_incomeSources12Months` | longtext | YES | - | NULL | - |
| `c_totalLoans12Months` | longtext | YES | - | NULL | - |
| `c_income_programs_key` | longtext | YES | - | NULL | - |
| `c_gainfulEmployment` | longtext | YES | - | NULL | - |
| `c_networkRelatives` | longtext | YES | - | NULL | - |
| `c_averageAnnualIncome` | longtext | YES | - | NULL | - |
| `c_monthlyExpenditure` | longtext | YES | - | NULL | - |
| `c_networksSupport` | longtext | YES | - | NULL | - |
| `c_creditDefault` | longtext | YES | - | NULL | - |
| `c_otherInputSupport` | longtext | YES | - | NULL | - |
| `c_programBenefits` | longtext | YES | - | NULL | - |
| `c_networkAssociations` | longtext | YES | - | NULL | - |
| `c_informalTransfers` | longtext | YES | - | NULL | - |
| `c_parent_id` | longtext | YES | - | NULL | - |
| `c_supportFrequency` | longtext | YES | - | NULL | - |
| `c_mainSourceIncome` | longtext | YES | - | NULL | - |
| `c_relativeSupport` | longtext | YES | - | NULL | - |
| `c_governmentEmployed` | longtext | YES | - | NULL | - |
| `c_everOnISP` | longtext | YES | - | NULL | - |
| `c_formalTransfers` | longtext | YES | - | NULL | - |
| `c_income_sources` | longtext | YES | - | NULL | - |
| `c_supportProgram` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_farmer_reg_approval`

- **Row Count:** 13
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_field2` | longtext | YES | - | NULL | - |
| `c_chief_approval` | longtext | YES | - | NULL | - |
| `c_field3` | longtext | YES | - | NULL | - |
| `c_application_id` | longtext | YES | - | NULL | - |
| `c_approval1_id` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "3c01b35c-8f87-41db-82ec-40808e710565",
  "dateCreated": "2025-04-20 13:58:19",
  "dateModified": "2025-04-20 13:58:19",
  "createdBy": "cat",
  "createdByName": "Cat Grant",
  "modifiedBy": "cat",
  "modifiedByName": "Cat Grant",
  "c_field2": null,
  "c_chief_approval": "Approved",
  "c_field3": "",
  "c_application_id": "3c01b35c-8f87-41db-82ec-40808e710565",
  "c_approval1_id": null
}
```

---

### Table: `app_fd_farmer_reg_decision`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_comments` | longtext | YES | - | NULL | - |
| `c_application_id` | longtext | YES | - | NULL | - |
| `c_officer_review` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_farmer_reg_record`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_residence_proof` | longtext | YES | - | NULL | - |
| `c_approval2_id` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_latitude` | longtext | YES | - | NULL | - |
| `c_ward` | longtext | YES | - | NULL | - |
| `c_primary_phone` | longtext | YES | - | NULL | - |
| `c_passport_photo` | longtext | YES | - | NULL | - |
| `c_vilage` | longtext | YES | - | NULL | - |
| `c_secondary_phone` | longtext | YES | - | NULL | - |
| `c_email` | longtext | YES | - | NULL | - |
| `c_document_type` | longtext | YES | - | NULL | - |
| `c_upload_date` | longtext | YES | - | NULL | - |
| `c_longitude` | longtext | YES | - | NULL | - |
| `c_elevation` | longtext | YES | - | NULL | - |
| `c_id_scan` | longtext | YES | - | NULL | - |
| `c_approval1_id` | longtext | YES | - | NULL | - |
| `c_primary_language` | longtext | YES | - | NULL | - |
| `c_location_description` | longtext | YES | - | NULL | - |
| `c_marital_status` | longtext | YES | - | NULL | - |
| `c_full_name` | longtext | YES | - | NULL | - |
| `c_gps_accuracy` | longtext | YES | - | NULL | - |
| `c_dob` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_application_number` | longtext | YES | - | NULL | - |
| `c_farming_experience` | longtext | YES | - | NULL | - |
| `c_status` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_farmer_reg_review`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_officer_review` | longtext | YES | - | NULL | - |
| `c_comments` | longtext | YES | - | NULL | - |
| `c_application_number` | longtext | YES | - | NULL | - |
| `c_approval2_id` | longtext | YES | - | NULL | - |
| `c_application_id` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "9f584ef5-6282-4f67-b4cb-6f21a23718bf",
  "dateCreated": "2025-04-20 12:35:49",
  "dateModified": "2025-04-20 12:35:49",
  "createdBy": "cat",
  "createdByName": "Cat Grant",
  "modifiedBy": "cat",
  "modifiedByName": "Cat Grant",
  "c_officer_review": "Reviewed",
  "c_comments": "",
  "c_application_number": null,
  "c_approval2_id": null,
  "c_application_id": "9f584ef5-6282-4f67-b4cb-6f21a23718bf"
}
```

---

### Table: `app_fd_farmer_registration`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_residence_proof` | longtext | YES | - | NULL | - |
| `c_elevation` | longtext | YES | - | NULL | - |
| `c_id_scan` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_latitude` | longtext | YES | - | NULL | - |
| `c_primary_language` | longtext | YES | - | NULL | - |
| `c_ward` | longtext | YES | - | NULL | - |
| `c_location_description` | longtext | YES | - | NULL | - |
| `c_primary_phone` | longtext | YES | - | NULL | - |
| `c_passport_photo` | longtext | YES | - | NULL | - |
| `c_marital_status` | longtext | YES | - | NULL | - |
| `c_full_name` | longtext | YES | - | NULL | - |
| `c_secondary_phone` | longtext | YES | - | NULL | - |
| `c_gps_accuracy` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | - | NULL | - |
| `c_farming_experience` | longtext | YES | - | NULL | - |
| `c_email` | longtext | YES | - | NULL | - |
| `c_document_type` | longtext | YES | - | NULL | - |
| `c_upload_date` | longtext | YES | - | NULL | - |
| `c_longitude` | longtext | YES | - | NULL | - |
| `c_status` | longtext | YES | - | NULL | - |
| `c_vilage` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_farmer_registry`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_agriculturalManagementSkills` | longtext | YES | - | NULL | - |
| `c_mainSourceLivelihood` | longtext | YES | - | NULL | - |
| `c_cropProduction` | longtext | YES | - | NULL | - |
| `c_mainSourceFarmLabour` | longtext | YES | - | NULL | - |
| `c_conservationPractices` | longtext | YES | - | NULL | - |
| `c_conservationPracticesOther` | longtext | YES | - | NULL | - |
| `c_agriculture_key` | longtext | YES | - | NULL | - |
| `c_livestockProduction` | longtext | YES | - | NULL | - |
| `c_hazardsExperienced` | longtext | YES | - | NULL | - |
| `c_mainSourceAgriculturalInfo` | longtext | YES | - | NULL | - |
| `c_hazardsShocks` | longtext | YES | - | NULL | - |
| `c_household_key` | longtext | YES | - | NULL | - |
| `c_canReadWrite` | longtext | YES | - | NULL | - |
| `c_parent_id` | longtext | YES | - | NULL | - |
| `c_copingMechanisms` | longtext | YES | - | NULL | - |
| `c_otherHazards` | longtext | YES | - | NULL | - |
| `c_shocks_hazards` | longtext | YES | - | NULL | - |
| `c_supportType` | longtext | YES | - | NULL | - |
| `c_registrationStatus` | longtext | YES | - | NULL | - |
| `c_incomeSources12Months` | longtext | YES | - | NULL | - |
| `c_gainfulEmployment` | longtext | YES | - | NULL | - |
| `c_declarationFullName` | longtext | YES | - | NULL | - |
| `c_declarationConsent` | longtext | YES | - | NULL | - |
| `c_registrationChannel` | longtext | YES | - | NULL | - |
| `c_creditDefault` | longtext | YES | - | NULL | - |
| `c_otherInputSupport` | longtext | YES | - | NULL | - |
| `c_programBenefits` | longtext | YES | - | NULL | - |
| `c_supportFrequency` | longtext | YES | - | NULL | - |
| `c_governmentEmployed` | longtext | YES | - | NULL | - |
| `c_everOnISP` | longtext | YES | - | NULL | - |
| `c_registrationStation` | longtext | YES | - | NULL | - |
| `c_formalTransfers` | longtext | YES | - | NULL | - |
| `c_totalLoans12Months` | longtext | YES | - | NULL | - |
| `c_networkRelatives` | longtext | YES | - | NULL | - |
| `c_averageAnnualIncome` | longtext | YES | - | NULL | - |
| `c_monthlyExpenditure` | longtext | YES | - | NULL | - |
| `c_field12` | longtext | YES | - | NULL | - |
| `c_networkAssociations` | longtext | YES | - | NULL | - |
| `c_beneficiaryCode` | longtext | YES | - | NULL | - |
| `c_informalTransfers` | longtext | YES | - | NULL | - |
| `c_field13` | longtext | YES | - | NULL | - |
| `c_mainSourceIncome` | longtext | YES | - | NULL | - |
| `c_relativeSupport` | longtext | YES | - | NULL | - |
| `c_hasLivestock` | longtext | YES | - | NULL | - |
| `c_crops_livestock_key` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "farmer-002",
  "dateCreated": "2025-09-22 18:30:38",
  "dateModified": "2025-09-22 18:30:38",
  "createdBy": "roleSystem",
  "createdByName": null,
  "modifiedBy": "roleSystem",
  "modifiedByName": null,
  "c_agriculturalManagementSkills": "college_diploma",
  "c_mainSourceLivelihood": "mixed",
  "c_cropProduction": "yes",
  "c_mainSourceFarmLabour": "family",
  "c_conservationPractices": null,
  "c_conservationPracticesOther": null,
  "c_agriculture_key": null,
  "c_livestockProduction": "1",
  "c_hazardsExperienced": null,
  "c_mainSourceAgriculturalInfo": "radio",
  "c_hazardsShocks": null,
  "c_household_key": null,
  "c_canReadWrite": "yes",
  "c_parent_id": "farmer-002",
  "c_copingMechanisms": "Used drought-resistant varieties, reduced area planted, sold some livestock to buy food",
  "c_otherHazards": null,
  "c_shocks_hazards": null,
  "c_supportType": "money;food",
  "c_registrationStatus": null,
  "c_incomeSources12Months": null,
  "c_gainfulEmployment": null,
  "c_declarationFullName": null,
  "c_declarationConsent": null,
  "c_registrationChannel": null,
  "c_creditDefault": null,
  "c_otherInputSupport": null,
  "c_programBenefits": null,
  "c_supportFrequency": "seasonal",
  "c_governmentEmployed": null,
  "c_everOnISP": "no",
  "c_registrationStation": null,
  "c_formalTransfers": null,
  "c_totalLoans12Months": null,
  "c_networkRelatives": null,
  "c_averageAnnualIncome": null,
  "c_monthlyExpenditure": null,
  "c_field12": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
  "c_networkAssociations": null,
  "c_beneficiaryCode": "BEN-2025-000002",
  "c_informalTransfers": null,
  "c_field13": null,
  "c_mainSourceIncome": null,
  "c_relativeSupport": null,
  "c_hasLivestock": null,
  "c_crops_livestock_key": null
}
```

---

### Table: `app_fd_farming_experience`

- **Row Count:** 2
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_experience_type` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "2fa94c3e-1a28-44e6-8526-fea4ff05729e",
  "dateCreated": "2025-03-05 19:53:29",
  "dateModified": "2025-03-05 19:53:29",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_experience_type": "Hobby"
}
```

---

### Table: `app_fd_farmland`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_plot_number` | longtext | YES | - | NULL | - |
| `c_landUseType` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_survey_reference` | longtext | YES | - | NULL | - |
| `c_ownershipStatus` | longtext | YES | - | NULL | - |
| `c_calculated_area` | longtext | YES | - | NULL | - |
| `c_survey_date` | longtext | YES | - | NULL | - |
| `c_surveyor_name` | longtext | YES | - | NULL | - |
| `c_plot_boundary` | longtext | YES | - | NULL | - |
| `c_spatial_files` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_farmland_usage`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_farmerId` | longtext | YES | - | NULL | - |
| `c_notes` | longtext | YES | - | NULL | - |
| `c_endDate` | longtext | YES | - | NULL | - |
| `c_documents` | longtext | YES | - | NULL | - |
| `c_farmlandId` | longtext | YES | - | NULL | - |
| `c_startDate` | longtext | YES | - | NULL | - |
| `c_rightType` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_farms_registry`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_basic_data` | longtext | YES | - | NULL | - |
| `c_household_data` | longtext | YES | - | NULL | - |
| `c_location_data` | longtext | YES | - | NULL | - |
| `c_activities_data` | longtext | YES | - | NULL | - |
| `c_declaration` | longtext | YES | - | NULL | - |
| `c_crops_livestock` | longtext | YES | - | NULL | - |
| `c_income_data` | longtext | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_supportType` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_mainSourceLivelihood` | longtext | YES | - | NULL | - |
| `c_extension_officer_name` | longtext | YES | - | NULL | - |
| `c_supportFrequency` | longtext | YES | - | NULL | - |
| `c_member_of_cooperative` | longtext | YES | - | NULL | - |
| `c_copingMechanisms` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | - | NULL | - |
| `c_first_name` | longtext | YES | - | NULL | - |
| `c_everOnISP` | longtext | YES | - | NULL | - |
| `c_preferred_language` | longtext | YES | - | NULL | - |
| `c_communityCouncil` | longtext | YES | - | NULL | - |
| `c_mainSourceFarmLabour` | longtext | YES | - | NULL | - |
| `c_last_name` | longtext | YES | - | NULL | - |
| `c_cooperative_name` | longtext | YES | - | NULL | - |
| `c_field12` | longtext | YES | - | NULL | - |
| `c_marital_status` | longtext | YES | - | NULL | - |
| `c_email_address` | longtext | YES | - | NULL | - |
| `c_beneficiaryCode` | longtext | YES | - | NULL | - |
| `c_canReadWrite` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_field9` | longtext | YES | - | NULL | - |
| `c_mobile_number` | longtext | YES | - | NULL | - |
| `c_residency` | longtext | YES | - | NULL | - |
| `c_registrationStatus` | longtext | YES | - | NULL | - |
| `c_gpsLongitude` | longtext | YES | - | NULL | - |
| `c_agriculturalManagementSkills` | longtext | YES | - | NULL | - |
| `c_distanceWaterSource` | longtext | YES | - | NULL | - |
| `c_gainfulEmployment` | longtext | YES | - | NULL | - |
| `c_declarationConsent` | longtext | YES | - | NULL | - |
| `c_livestockProduction` | longtext | YES | - | NULL | - |
| `c_hazardsExperienced` | longtext | YES | - | NULL | - |
| `c_creditDefault` | longtext | YES | - | NULL | - |
| `c_otherInputSupport` | longtext | YES | - | NULL | - |
| `c_distanceLivestockMarket` | longtext | YES | - | NULL | - |
| `c_governmentEmployed` | longtext | YES | - | NULL | - |
| `c_otherHazards` | longtext | YES | - | NULL | - |
| `c_registrationStation` | longtext | YES | - | NULL | - |
| `c_ownedRentedLand` | longtext | YES | - | NULL | - |
| `c_totalLoans12Months` | longtext | YES | - | NULL | - |
| `c_conservationPractices` | longtext | YES | - | NULL | - |
| `c_conservationPracticesOther` | longtext | YES | - | NULL | - |
| `c_access_to_services` | longtext | YES | - | NULL | - |
| `c_networkRelatives` | longtext | YES | - | NULL | - |
| `c_monthlyExpenditure` | longtext | YES | - | NULL | - |
| `c_networkAssociations` | longtext | YES | - | NULL | - |
| `c_informalTransfers` | longtext | YES | - | NULL | - |
| `c_field13` | longtext | YES | - | NULL | - |
| `c_distancePrimarySchool` | longtext | YES | - | NULL | - |
| `c_yearsInArea` | longtext | YES | - | NULL | - |
| `c_distancePublicTransport` | longtext | YES | - | NULL | - |
| `c_distancePublicHospital` | longtext | YES | - | NULL | - |
| `c_totalAvailableLand` | longtext | YES | - | NULL | - |
| `c_conservationAgricultureLand` | longtext | YES | - | NULL | - |
| `c_distanceAgriculturalMarket` | longtext | YES | - | NULL | - |
| `c_cultivatedLand` | longtext | YES | - | NULL | - |
| `c_incomeSources12Months` | longtext | YES | - | NULL | - |
| `c_declarationFullName` | longtext | YES | - | NULL | - |
| `c_registrationChannel` | longtext | YES | - | NULL | - |
| `c_mainSourceAgriculturalInfo` | longtext | YES | - | NULL | - |
| `c_programBenefits` | longtext | YES | - | NULL | - |
| `c_gpsLatitude` | longtext | YES | - | NULL | - |
| `c_formalTransfers` | longtext | YES | - | NULL | - |
| `c_cropProduction` | longtext | YES | - | NULL | - |
| `c_averageAnnualIncome` | longtext | YES | - | NULL | - |
| `c_agroEcologicalZone` | longtext | YES | - | NULL | - |
| `c_mainSourceIncome` | longtext | YES | - | NULL | - |
| `c_relativeSupport` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "farmer-002",
  "dateCreated": "2025-09-22 18:30:38",
  "dateModified": "2025-09-24 23:27:56",
  "createdBy": "roleSystem",
  "createdByName": null,
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_basic_data": "farmer-002",
  "c_household_data": "",
  "c_location_data": "",
  "c_activities_data": "",
  "c_declaration": "",
  "c_crops_livestock": "",
  "c_income_data": "",
  "c_national_id": null,
  "c_supportType": null,
  "c_date_of_birth": null,
  "c_mainSourceLivelihood": null,
  "c_extension_officer_name": null,
  "c_supportFrequency": null,
  "c_member_of_cooperative": null,
  "c_copingMechanisms": null,
  "c_village": null,
  "c_first_name": null,
  "c_everOnISP": null,
  "c_preferred_language": null,
  "c_communityCouncil": null,
  "c_mainSourceFarmLabour": null,
  "c_last_name": null,
  "c_cooperative_name": null,
  "c_field12": null,
  "c_marital_status": null,
  "c_email_address": null,
  "c_beneficiaryCode": null,
  "c_canReadWrite": null,
  "c_district": null,
  "c_field9": null,
  "c_mobile_number": null,
  "c_residency": null,
  "c_registrationStatus": null,
  "c_gpsLongitude": null,
  "c_agriculturalManagementSkills": null,
  "c_distanceWaterSource": null,
  "c_gainfulEmployment": null,
  "c_declarationConsent": null,
  "c_livestockProduction": null,
  "c_hazardsExperienced": null,
  "c_creditDefault": null,
  "c_otherInputSupport": null,
  "c_distanceLivestockMarket": null,
  "c_governmentEmployed": null,
  "c_otherHazards": null,
  "c_registrationStation": null,
  "c_ownedRentedLand": null,
  "c_totalLoans12Months": null,
  "c_conservationPractices": null,
  "c_conservationPracticesOther": null,
  "c_access_to_services": null,
  "c_networkRelatives": null,
  "c_monthlyExpenditure": null,
  "c_networkAssociations": null,
  "c_informalTransfers": null,
  "c_field13": null,
  "c_distancePrimarySchool": null,
  "c_yearsInArea": null,
  "c_distancePublicTransport": null,
  "c_distancePublicHospital": null,
  "c_totalAvailableLand": null,
  "c_conservationAgricultureLand": null,
  "c_distanceAgriculturalMarket": null,
  "c_cultivatedLand": null,
  "c_incomeSources12Months": null,
  "c_declarationFullName": null,
  "c_registrationChannel": null,
  "c_mainSourceAgriculturalInfo": null,
  "c_programBenefits": null,
  "c_gpsLatitude": null,
  "c_formalTransfers": null,
  "c_cropProduction": null,
  "c_averageAnnualIncome": null,
  "c_agroEcologicalZone": null,
  "c_mainSourceIncome": null,
  "c_relativeSupport": null
}
```

---

### Table: `app_fd_fo_farmer_reg`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_residence_proof` | longtext | YES | - | NULL | - |
| `c_elevation` | longtext | YES | - | NULL | - |
| `c_id_scan` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_latitude` | longtext | YES | - | NULL | - |
| `c_primary_language` | longtext | YES | - | NULL | - |
| `c_location_description` | longtext | YES | - | NULL | - |
| `c_primary_phone` | longtext | YES | - | NULL | - |
| `c_passport_photo` | longtext | YES | - | NULL | - |
| `c_marital_status` | longtext | YES | - | NULL | - |
| `c_full_name` | longtext | YES | - | NULL | - |
| `c_secondary_phone` | longtext | YES | - | NULL | - |
| `c_gps_accuracy` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_application_number` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | - | NULL | - |
| `c_farming_experience` | longtext | YES | - | NULL | - |
| `c_email` | longtext | YES | - | NULL | - |
| `c_document_type` | longtext | YES | - | NULL | - |
| `c_upload_date` | longtext | YES | - | NULL | - |
| `c_longitude` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "444f6f8c-6aa9-46e2-a91e-f04f908275c7",
  "dateCreated": "2025-07-07 14:47:00",
  "dateModified": "2025-07-07 14:47:00",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_national_id": "111",
  "c_residence_proof": "",
  "c_elevation": "",
  "c_id_scan": "",
  "c_gender": "male",
  "c_date_of_birth": "2025-07-01",
  "c_latitude": "",
  "c_primary_language": "",
  "c_location_description": "",
  "c_primary_phone": "",
  "c_passport_photo": "",
  "c_marital_status": "married_civil",
  "c_full_name": "Peeter Meeter",
  "c_secondary_phone": "",
  "c_gps_accuracy": "",
  "c_district": "D01",
  "c_application_number": "AP-000061",
  "c_village": "",
  "c_farming_experience": "E01",
  "c_email": "",
  "c_document_type": "form_c",
  "c_upload_date": "",
  "c_longitude": ""
}
```

---

### Table: `app_fd_fo_household_reg`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_occupation` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_income_reliability` | longtext | YES | - | NULL | - |
| `c_has_water` | longtext | YES | - | NULL | - |
| `c_assets` | longtext | YES | - | NULL | - |
| `c_wall_material` | longtext | YES | - | NULL | - |
| `c_member_count` | longtext | YES | - | NULL | - |
| `c_relationship` | longtext | YES | - | NULL | - |
| `c_has_electricity` | longtext | YES | - | NULL | - |
| `c_disability_status` | longtext | YES | - | NULL | - |
| `c_has_remittances` | longtext | YES | - | NULL | - |
| `c_room_count` | longtext | YES | - | NULL | - |
| `c_income_source` | longtext | YES | - | NULL | - |
| `c_monthly_income` | longtext | YES | - | NULL | - |
| `c_poverty_score` | longtext | YES | - | NULL | - |
| `c_member_name` | longtext | YES | - | NULL | - |
| `c_registration_date` | longtext | YES | - | NULL | - |
| `c_primary_income` | longtext | YES | - | NULL | - |
| `c_roof_material` | longtext | YES | - | NULL | - |
| `c_floor_material` | longtext | YES | - | NULL | - |
| `c_secondary_income` | longtext | YES | - | NULL | - |
| `c_remittance_amount` | longtext | YES | - | NULL | - |
| `c_education_level` | longtext | YES | - | NULL | - |
| `c_dwelling_type` | longtext | YES | - | NULL | - |
| `c_household_ref` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "c446e4ec-e2c9-4027-9205-1307ed73acdc",
  "dateCreated": "2025-07-07 14:38:46",
  "dateModified": "2025-07-07 14:38:46",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_occupation": "",
  "c_gender": "female",
  "c_date_of_birth": "",
  "c_income_reliability": "farming_income",
  "c_has_water": "",
  "c_assets": "",
  "c_wall_material": "",
  "c_member_count": "",
  "c_relationship": "",
  "c_has_electricity": "",
  "c_disability_status": "",
  "c_has_remittances": "",
  "c_room_count": "",
  "c_income_source": "",
  "c_monthly_income": "",
  "c_poverty_score": "",
  "c_member_name": "",
  "c_registration_date": "",
  "c_primary_income": "",
  "c_roof_material": "",
  "c_floor_material": "",
  "c_secondary_income": "",
  "c_remittance_amount": "",
  "c_education_level": "",
  "c_dwelling_type": "rondavel_traditional",
  "c_household_ref": ""
}
```

---

### Table: `app_fd_household_members`

- **Row Count:** 3
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_chronicallyIll` | longtext | YES | - | NULL | - |
| `c_participatesInAgriculture` | longtext | YES | - | NULL | - |
| `c_orphanhoodStatus` | longtext | YES | - | NULL | - |
| `c_farmer_id` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_disability` | longtext | YES | - | NULL | - |
| `c_sex` | longtext | YES | - | NULL | - |
| `c_memberName` | longtext | YES | - | NULL | - |
| `c_relationship` | longtext | YES | - | NULL | - |
| `c_parentId` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "57e0513f-70d2-4122-bf69-f3b30f1bedc1",
  "dateCreated": "2025-09-22 18:30:40",
  "dateModified": "2025-09-22 18:30:40",
  "createdBy": "roleSystem",
  "createdByName": null,
  "modifiedBy": "roleSystem",
  "modifiedByName": null,
  "c_chronicallyIll": "2",
  "c_participatesInAgriculture": "2",
  "c_orphanhoodStatus": "both_alive",
  "c_farmer_id": "farmer-002",
  "c_date_of_birth": "2014-09-08",
  "c_disability": "none",
  "c_sex": "female",
  "c_memberName": "Motlomelo, Naleli",
  "c_relationship": null,
  "c_parentId": null
}
```

---

### Table: `app_fd_household_reg`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_occupation` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_income_reliability` | longtext | YES | - | NULL | - |
| `c_has_water` | longtext | YES | - | NULL | - |
| `c_assets` | longtext | YES | - | NULL | - |
| `c_wall_material` | longtext | YES | - | NULL | - |
| `c_member_count` | longtext | YES | - | NULL | - |
| `c_relationship` | longtext | YES | - | NULL | - |
| `c_has_electricity` | longtext | YES | - | NULL | - |
| `c_disability_status` | longtext | YES | - | NULL | - |
| `c_has_remittances` | longtext | YES | - | NULL | - |
| `c_room_count` | longtext | YES | - | NULL | - |
| `c_income_source` | longtext | YES | - | NULL | - |
| `c_monthly_income` | longtext | YES | - | NULL | - |
| `c_poverty_score` | longtext | YES | - | NULL | - |
| `c_member_name` | longtext | YES | - | NULL | - |
| `c_registration_date` | longtext | YES | - | NULL | - |
| `c_primary_income` | longtext | YES | - | NULL | - |
| `c_roof_material` | longtext | YES | - | NULL | - |
| `c_floor_material` | longtext | YES | - | NULL | - |
| `c_secondary_income` | longtext | YES | - | NULL | - |
| `c_remittance_amount` | longtext | YES | - | NULL | - |
| `c_education_level` | longtext | YES | - | NULL | - |
| `c_dwelling_type` | longtext | YES | - | NULL | - |
| `c_household_ref` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "c519017a-b3dd-438e-bab2-69106b695ccf",
  "dateCreated": "2025-02-09 02:21:26",
  "dateModified": "2025-02-09 02:21:34",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_occupation": "",
  "c_gender": "female",
  "c_date_of_birth": "",
  "c_income_reliability": "farming_income",
  "c_has_water": "",
  "c_assets": "",
  "c_wall_material": "",
  "c_member_count": "",
  "c_relationship": "",
  "c_has_electricity": "",
  "c_disability_status": "",
  "c_has_remittances": "",
  "c_room_count": "",
  "c_income_source": "",
  "c_monthly_income": "",
  "c_poverty_score": "",
  "c_member_name": "",
  "c_registration_date": "2025-02-11",
  "c_primary_income": "",
  "c_roof_material": "",
  "c_floor_material": "",
  "c_secondary_income": "",
  "c_remittance_amount": "",
  "c_education_level": "",
  "c_dwelling_type": "rondavel_traditional",
  "c_household_ref": "11"
}
```

---

### Table: `app_fd_income_source`

- **Row Count:** 10
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_code` | longtext | YES | - | NULL | - |
| `c_name` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "0fb9d650-fe6a-4553-a740-8577288d5825",
  "dateCreated": "2025-09-21 17:31:46",
  "dateModified": "2025-09-21 17:31:46",
  "createdBy": "roleAnonymous",
  "createdByName": null,
  "modifiedBy": "roleAnonymous",
  "modifiedByName": null,
  "c_code": "family_support",
  "c_name": "Support from family or non-family"
}
```

---

### Table: `app_fd_livestock_details`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_numberOfFemale` | longtext | YES | - | NULL | - |
| `c_farmer_id` | longtext | YES | - | NULL | - |
| `c_livestockType` | longtext | YES | - | NULL | - |
| `c_numberOfMale` | longtext | YES | - | NULL | - |
| `c_parentId` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_livestock_type`

- **Row Count:** 18
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_code` | longtext | YES | - | NULL | - |
| `c_name` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "11ed9d5d-51eb-4c03-8568-e056198e9c8c",
  "dateCreated": "2025-09-21 17:31:44",
  "dateModified": "2025-09-21 17:31:44",
  "createdBy": "roleAnonymous",
  "createdByName": null,
  "modifiedBy": "roleAnonymous",
  "modifiedByName": null,
  "c_code": "pigs",
  "c_name": "Pigs"
}
```

---

### Table: `app_fd_moa_bo_farmer_reg`

- **Row Count:** 2
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_residence_proof` | longtext | YES | - | NULL | - |
| `c_elevation` | longtext | YES | - | NULL | - |
| `c_id_scan` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_latitude` | longtext | YES | - | NULL | - |
| `c_primary_language` | longtext | YES | - | NULL | - |
| `c_location_description` | longtext | YES | - | NULL | - |
| `c_application_id` | longtext | YES | - | NULL | - |
| `c_primary_phone` | longtext | YES | - | NULL | - |
| `c_passport_photo` | longtext | YES | - | NULL | - |
| `c_vilage` | longtext | YES | - | NULL | - |
| `c_marital_status` | longtext | YES | - | NULL | - |
| `c_full_name` | longtext | YES | - | NULL | - |
| `c_secondary_phone` | longtext | YES | - | NULL | - |
| `c_gps_accuracy` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_farming_experience` | longtext | YES | - | NULL | - |
| `c_email` | longtext | YES | - | NULL | - |
| `c_document_type` | longtext | YES | - | NULL | - |
| `c_upload_date` | longtext | YES | - | NULL | - |
| `c_longitude` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | - | NULL | - |
| `c_application_number` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "8f80502c-aa37-4150-b3d2-9f6a4a29f33c",
  "dateCreated": "2025-04-05 14:08:36",
  "dateModified": "2025-04-05 14:08:36",
  "createdBy": "roleAnonymous",
  "createdByName": null,
  "modifiedBy": "roleAnonymous",
  "modifiedByName": null,
  "c_national_id": "",
  "c_residence_proof": "",
  "c_elevation": "",
  "c_id_scan": "",
  "c_gender": "",
  "c_date_of_birth": "",
  "c_latitude": "",
  "c_primary_language": "",
  "c_location_description": "",
  "c_application_id": "",
  "c_primary_phone": "",
  "c_passport_photo": "",
  "c_vilage": null,
  "c_marital_status": "",
  "c_full_name": "",
  "c_secondary_phone": "",
  "c_gps_accuracy": "",
  "c_district": "",
  "c_farming_experience": "",
  "c_email": "",
  "c_document_type": "",
  "c_upload_date": "",
  "c_longitude": "",
  "c_village": "",
  "c_application_number": null
}
```

---

### Table: `app_fd_moa_farmer_reg`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_residence_proof` | longtext | YES | - | NULL | - |
| `c_elevation` | longtext | YES | - | NULL | - |
| `c_id_scan` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_latitude` | longtext | YES | - | NULL | - |
| `c_primary_language` | longtext | YES | - | NULL | - |
| `c_ward` | longtext | YES | - | NULL | - |
| `c_location_description` | longtext | YES | - | NULL | - |
| `c_primary_phone` | longtext | YES | - | NULL | - |
| `c_passport_photo` | longtext | YES | - | NULL | - |
| `c_vilage` | longtext | YES | - | NULL | - |
| `c_marital_status` | longtext | YES | - | NULL | - |
| `c_full_name` | longtext | YES | - | NULL | - |
| `c_secondary_phone` | longtext | YES | - | NULL | - |
| `c_gps_accuracy` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_farming_experience` | longtext | YES | - | NULL | - |
| `c_email` | longtext | YES | - | NULL | - |
| `c_document_type` | longtext | YES | - | NULL | - |
| `c_upload_date` | longtext | YES | - | NULL | - |
| `c_longitude` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | - | NULL | - |
| `c_application_number` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "9fb83c55-700b-4abf-885b-482da256fafc",
  "dateCreated": "2025-03-29 21:42:38",
  "dateModified": "2025-04-04 19:07:47",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_national_id": "28228",
  "c_residence_proof": "",
  "c_elevation": "",
  "c_id_scan": "",
  "c_gender": "female",
  "c_date_of_birth": "2025-03-02",
  "c_latitude": "",
  "c_primary_language": "",
  "c_ward": null,
  "c_location_description": "",
  "c_primary_phone": "88888-222",
  "c_passport_photo": "",
  "c_vilage": "",
  "c_marital_status": "married_customary",
  "c_full_name": "Lucia Hard",
  "c_secondary_phone": "7777-444",
  "c_gps_accuracy": "",
  "c_district": "88bc97b5-fe10-463e-85d1-3219e7b1495d",
  "c_farming_experience": "E01",
  "c_email": "email",
  "c_document_type": "form_c",
  "c_upload_date": "",
  "c_longitude": "",
  "c_village": "9cc040b4-6760-4f1c-9631-725ab3a7049d",
  "c_application_number": "AP-000001"
}
```

---

### Table: `app_fd_reg_farm_form`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_plot_number` | longtext | YES | - | NULL | - |
| `c_survey_reference_number` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_land_use_type` | longtext | YES | - | NULL | - |
| `c_calculated_area` | longtext | YES | - | NULL | - |
| `c_survey_date` | longtext | YES | - | NULL | - |
| `c_spatial_data_files` | longtext | YES | - | NULL | - |
| `c_surveyor_name` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | - | NULL | - |
| `c_plot_boundary` | longtext | YES | - | NULL | - |
| `c_ownership_status` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_reg_farm_land_reg`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_end_date` | longtext | YES | - | NULL | - |
| `c_additional_notes` | longtext | YES | - | NULL | - |
| `c_supporting_documents` | longtext | YES | - | NULL | - |
| `c_farmer` | longtext | YES | - | NULL | - |
| `c_type_of_right` | longtext | YES | - | NULL | - |
| `c_farmland` | longtext | YES | - | NULL | - |
| `c_start_date` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_reg_farmer_reg`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_residence_proof` | longtext | YES | - | NULL | - |
| `c_elevation` | longtext | YES | - | NULL | - |
| `c_id_scan` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_latitude` | longtext | YES | - | NULL | - |
| `c_primary_language` | longtext | YES | - | NULL | - |
| `c_location_description` | longtext | YES | - | NULL | - |
| `c_application_id` | longtext | YES | - | NULL | - |
| `c_primary_phone` | longtext | YES | - | NULL | - |
| `c_passport_photo` | longtext | YES | - | NULL | - |
| `c_vilage` | longtext | YES | - | NULL | - |
| `c_marital_status` | longtext | YES | - | NULL | - |
| `c_full_name` | longtext | YES | - | NULL | - |
| `c_secondary_phone` | longtext | YES | - | NULL | - |
| `c_gps_accuracy` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_application_number` | longtext | YES | - | NULL | - |
| `c_farming_experience` | longtext | YES | - | NULL | - |
| `c_email` | longtext | YES | - | NULL | - |
| `c_document_type` | longtext | YES | - | NULL | - |
| `c_upload_date` | longtext | YES | - | NULL | - |
| `c_longitude` | longtext | YES | - | NULL | - |
| `c_village` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_registry_inspection`

- **Row Count:** 0
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_approvalNotes` | longtext | YES | - | NULL | - |
| `c_inspectionPhotos` | longtext | YES | - | NULL | - |
| `c_identityVerification` | longtext | YES | - | NULL | - |
| `c_farmerVerificationNotes` | longtext | YES | - | NULL | - |
| `c_landUseVerification` | longtext | YES | - | NULL | - |
| `c_inspector` | longtext | YES | - | NULL | - |
| `c_farmlandUsageId` | longtext | YES | - | NULL | - |
| `c_inspectionId` | longtext | YES | - | NULL | - |
| `c_rightsVerificationNotes` | longtext | YES | - | NULL | - |
| `c_registryOfficerApproval` | longtext | YES | - | NULL | - |
| `c_landAdministratorApproval` | longtext | YES | - | NULL | - |
| `c_documentVerification` | longtext | YES | - | NULL | - |
| `c_boundaryVerification` | longtext | YES | - | NULL | - |
| `c_inspectionDate` | longtext | YES | - | NULL | - |
| `c_inspection_date` | longtext | YES | - | NULL | - |
| `c_national_id` | longtext | YES | - | NULL | - |
| `c_end_date` | longtext | YES | - | NULL | - |
| `c_occupation` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_years_experience` | longtext | YES | - | NULL | - |
| `c_date_of_birth` | longtext | YES | - | NULL | - |
| `c_local_authority` | longtext | YES | - | NULL | - |
| `c_plot_boundary` | longtext | YES | - | NULL | - |
| `c_spatial_files` | longtext | YES | - | NULL | - |
| `c_primary_phone` | longtext | YES | - | NULL | - |
| `c_discrepancy_notes` | longtext | YES | - | NULL | - |
| `c_additional_notes` | longtext | YES | - | NULL | - |
| `c_supporting_documents` | longtext | YES | - | NULL | - |
| `c_land_commissioner` | longtext | YES | - | NULL | - |
| `c_inspection_id` | longtext | YES | - | NULL | - |
| `c_secondary_phone` | longtext | YES | - | NULL | - |
| `c_surname` | longtext | YES | - | NULL | - |
| `c_land_administration` | longtext | YES | - | NULL | - |
| `c_land_use_type` | longtext | YES | - | NULL | - |
| `c_calculated_area` | longtext | YES | - | NULL | - |
| `c_first_name` | longtext | YES | - | NULL | - |
| `c_email` | longtext | YES | - | NULL | - |
| `c_irrigation_methods` | longtext | YES | - | NULL | - |
| `c_start_date` | longtext | YES | - | NULL | - |
| `c_postal_address` | longtext | YES | - | NULL | - |
| `c_plot_number` | longtext | YES | - | NULL | - |
| `c_survey_reference` | longtext | YES | - | NULL | - |
| `c_middle_name` | longtext | YES | - | NULL | - |
| `c_available_facilities` | longtext | YES | - | NULL | - |
| `c_inspection_photos` | longtext | YES | - | NULL | - |
| `c_inspector_name` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | MUL | NULL | - |
| `c_right_type` | longtext | YES | - | NULL | - |
| `c_survey_date` | longtext | YES | - | NULL | - |
| `c_surveyor_name` | longtext | YES | - | NULL | - |
| `c_ownership_status` | longtext | YES | - | NULL | - |
| `c_inspection_act_nr` | longtext | YES | - | NULL | - |

---

### Table: `app_fd_sample_farm_land`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_plot_number` | longtext | YES | - | NULL | - |
| `c_geo_json` | longtext | YES | - | NULL | - |
| `c_district` | longtext | YES | - | NULL | - |
| `c_survey_reference` | longtext | YES | - | NULL | - |
| `c_land_use_type` | longtext | YES | - | NULL | - |
| `c_calculated_area` | longtext | YES | - | NULL | - |
| `c_survey_date` | longtext | YES | - | NULL | - |
| `c_surveyor_name` | longtext | YES | - | NULL | - |
| `c_spatial_files` | longtext | YES | - | NULL | - |
| `c_ownership_status` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "afbecb57-71c9-456d-be57-0c0b374b63c8",
  "dateCreated": "2024-12-19 00:10:19",
  "dateModified": "2024-12-19 00:10:19",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_plot_number": "1111",
  "c_geo_json": "",
  "c_district": null,
  "c_survey_reference": "",
  "c_land_use_type": null,
  "c_calculated_area": "",
  "c_survey_date": "",
  "c_surveyor_name": "",
  "c_spatial_files": "",
  "c_ownership_status": null
}
```

---

### Table: `app_fd_sample_farmer_form`

- **Row Count:** 1
- **Primary Key:** `id`

#### Columns:

| Column Name | Type | Nullable | Key | Default | Extra |
|-------------|------|----------|-----|---------|-------|
| `id` | varchar(255) | NO | PRI | NULL | - |
| `dateCreated` | datetime(6) | YES | MUL | NULL | - |
| `dateModified` | datetime(6) | YES | - | NULL | - |
| `createdBy` | varchar(255) | YES | MUL | NULL | - |
| `createdByName` | varchar(255) | YES | - | NULL | - |
| `modifiedBy` | varchar(255) | YES | - | NULL | - |
| `modifiedByName` | varchar(255) | YES | - | NULL | - |
| `c_firstName` | longtext | YES | - | NULL | - |
| `c_primaryPhone` | longtext | YES | - | NULL | - |
| `c_postalAddress` | longtext | YES | - | NULL | - |
| `c_occupation` | longtext | YES | - | NULL | - |
| `c_nationalId` | longtext | YES | - | NULL | - |
| `c_gender` | longtext | YES | - | NULL | - |
| `c_surname` | longtext | YES | - | NULL | - |
| `c_middleName` | longtext | YES | - | NULL | - |
| `c_dateOfBirth` | longtext | YES | - | NULL | - |
| `c_yearsExperience` | longtext | YES | - | NULL | - |
| `c_secondaryPhone` | longtext | YES | - | NULL | - |
| `c_email` | longtext | YES | - | NULL | - |

#### Sample Data:

```json
{
  "id": "33c7b78a-2f22-4f89-99e9-88671566ff2a",
  "dateCreated": "2024-12-18 23:39:28",
  "dateModified": "2024-12-18 23:39:28",
  "createdBy": "admin",
  "createdByName": "Admin Admin",
  "modifiedBy": "admin",
  "modifiedByName": "Admin Admin",
  "c_firstName": "Aare",
  "c_primaryPhone": "",
  "c_postalAddress": "",
  "c_occupation": "manager",
  "c_nationalId": "",
  "c_gender": "",
  "c_surname": "aaa",
  "c_middleName": "",
  "c_dateOfBirth": "2024-12-10",
  "c_yearsExperience": "",
  "c_secondaryPhone": "",
  "c_email": ""
}
```

---