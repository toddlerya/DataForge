SELECT "name",
       ename,
       identifier,
       description,
       field_type,
       dictkey,
       is_query,
       is_multi_value,
       field_length,
       element_code,
       determiner_code,
       is_required
FROM public.base_field_info
where ename IN ('ISP_TYPE')
  AND length(name) != char_length(name)
limit 10;


SELECT name, COUNT(*) AS name_count
FROM public.base_field_info
WHERE ename IN ('ISP_TYPE')
  AND name ~ '[\u4e00-\u9fa5]'
GROUP BY name
ORDER BY name_count DESC
LIMIT 1;

SELECT identifier, COUNT(*) AS identifier_count
FROM public.base_field_info
WHERE ename IN ('ISP_TYPE')
GROUP BY identifier
ORDER BY identifier_count DESC
LIMIT 1;

SELECT description, COUNT(*) AS description_count
FROM public.base_field_info
WHERE ename IN ('ISP_TYPE')
  AND description ~ '[\u4e00-\u9fa5]'
GROUP BY description
ORDER BY description_count DESC
LIMIT 1;

SELECT bft.field_type, COUNT(*) AS field_type_count
FROM public.base_field_info AS bfi
         JOIN public.base_field_type AS bft ON bfi.field_type = bft.code
WHERE ename IN ('ISP_TYPE')
GROUP BY bft.field_type
ORDER BY field_type_count DESC
LIMIT 1;

SELECT dictkey, COUNT(*) AS dictkey_count
FROM public.base_field_info
WHERE ename IN ('ISP_TYPE')
  AND dictkey IS NOT NULL
  AND dictkey != ''
GROUP BY dictkey
ORDER BY dictkey_count DESC
LIMIT 1;

SELECT is_query, COUNT(*) AS is_query_count
FROM public.base_field_info
WHERE ename IN ('ISP_TYPE')
  AND is_query IS NOT NULL
GROUP BY is_query
ORDER BY is_query_count DESC
LIMIT 1;



SELECT name_sub.name                     AS name,
       name_sub.name_count               AS name_count,
       identifier_sub.identifier         AS identifier,
       identifier_sub.identifier_count   AS identifier_count,
       description_sub.description       AS description,
       description_sub.description_count AS description_count,
       field_type_sub.field_type         AS field_type,
       field_type_sub.field_type_count   AS field_type_count,
       dictkey_sub.dictkey               AS dictkey,
       dictkey_sub.dictkey_count         AS dictkey_count
FROM (SELECT name, COUNT(*) AS name_count
      FROM public.base_field_info
      WHERE ename = 'ISP_TYPE'
        AND name ~ '[\u4e00-\u9fa5]'
      GROUP BY name
      ORDER BY name_count DESC
      LIMIT 1) AS name_sub

         CROSS JOIN (SELECT identifier, COUNT(*) AS identifier_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE'
                     GROUP BY identifier
                     ORDER BY identifier_count DESC
                     LIMIT 1) AS identifier_sub

         CROSS JOIN (SELECT description, COUNT(*) AS description_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE'
                       AND description ~ '[\u4e00-\u9fa5]'
                     GROUP BY description
                     ORDER BY description_count DESC
                     LIMIT 1) AS description_sub

         CROSS JOIN (SELECT bft.field_type, COUNT(*) AS field_type_count
                     FROM public.base_field_info AS bfi
                              JOIN public.base_field_type AS bft ON bfi.field_type = bft.code
                     WHERE bfi.ename = 'ISP_TYPE'
                     GROUP BY bft.field_type
                     ORDER BY field_type_count DESC
                     LIMIT 1) AS field_type_sub

         CROSS JOIN (SELECT dictkey, COUNT(*) AS dictkey_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE'
                       AND dictkey IS NOT NULL
                       AND dictkey != ''
                     GROUP BY dictkey
                     ORDER BY dictkey_count DESC
                     LIMIT 1) AS dictkey_sub;



SELECT name_sub.name                                                             AS name,
       name_sub.name_count                                                       AS name_count,
       ROUND(name_sub.name_count * 100.0 / total_sub.total_count, 2)             AS name_percentage,
       identifier_sub.identifier                                                 AS identifier,
       identifier_sub.identifier_count                                           AS identifier_count,
       ROUND(identifier_sub.identifier_count * 100.0 / total_sub.total_count, 2) AS identifier_percentage,
       description_sub.description                                               AS description,
       description_sub.description_count                                         AS description_count,
       ROUND(description_sub.description_count * 100.0 / total_sub.total_count,
             2)                                                                  AS description_percentage,
       field_type_sub.field_type_name                                            AS field_type_name,
       field_type_sub.field_type_count                                           AS field_type_count,
       ROUND(field_type_sub.field_type_count * 100.0 / total_sub.total_count,
             2)                                                                  AS field_type_percentage,
       dictkey_sub.dictkey                                                       AS dictkey,
       dictkey_sub.dictkey_count                                                 AS dictkey_count,
       ROUND(dictkey_sub.dictkey_count * 100.0 / total_sub.total_count,
             2)                                                                  AS dictkey_percentage,
       field_length_sub.field_length                                             AS field_length,
       field_length_sub.field_length_count                                       AS field_length_count,
       ROUND(field_length_sub.field_length_count * 100.0 / total_sub.total_count,
             2)                                                                  AS field_length_percentage,
       element_code_sub.element_code_name                                        AS element_code_name,
       element_code_sub.element_code_count                                       AS field_length_count,
       ROUND(element_code_sub.element_code_count * 100.0 / total_sub.total_count,
             2)                                                                  AS field_length_percentage,
       determiner_code_sub.determiner_code_name                                  AS determiner_code_name,
       determiner_code_sub.determiner_code_count                                 AS determiner_code_count,
       ROUND(determiner_code_sub.determiner_code_count * 100.0 / total_sub.total_count,
             2)                                                                  AS determiner_code_percentage,
       structure_type_sub.structure_type                                         AS structure_type,
       structure_type_sub.structure_type_count                                   AS structure_type_count,
       ROUND(structure_type_sub.structure_type_count * 100.0 / total_sub.total_count,
             2)                                                                  AS structure_type_percentage,
       is_multi_value_sub.is_multi_value                                         AS is_multi_value,
       is_multi_value_sub.is_multi_value_count                                   AS is_multi_value_count,
       ROUND(is_multi_value_sub.is_multi_value_count * 100.0 / total_sub.total_count,
             2)                                                                  AS is_multi_value_percentage,
       is_required_sub.is_required                                               AS is_required,
       is_required_sub.is_required_count                                         AS is_required_count,
       ROUND(is_required_sub.is_required_count * 100.0 / total_sub.total_count,
             2)                                                                  AS is_required_percentage
FROM (SELECT name, COUNT(*) AS name_count
      FROM public.base_field_info
      WHERE ename = 'ISP_TYPE'
        AND name ~ '[\u4e00-\u9fa5]'
      GROUP BY name
      ORDER BY name_count DESC
      LIMIT 1) AS name_sub
         CROSS JOIN (SELECT identifier, COUNT(*) AS identifier_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE'
                     GROUP BY identifier
                     ORDER BY identifier_count DESC
                     LIMIT 1) AS identifier_sub
         CROSS JOIN (SELECT description, COUNT(*) AS description_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE'
                       AND description ~ '[\u4e00-\u9fa5]'
                     GROUP BY description
                     ORDER BY description_count DESC
                     LIMIT 1) AS description_sub
         CROSS JOIN (SELECT bft.field_type AS field_type_name, COUNT(*) AS field_type_count
                     FROM public.base_field_info AS bfi
                              JOIN public.base_field_type AS bft ON bfi.field_type = bft.code
                     WHERE bfi.ename = 'ISP_TYPE'
                     GROUP BY bft.field_type
                     ORDER BY field_type_count DESC
                     LIMIT 1) AS field_type_sub
         CROSS JOIN (SELECT dictkey, COUNT(*) AS dictkey_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE'
                       AND dictkey IS NOT NULL
                       AND dictkey != ''
                     GROUP BY dictkey
                     ORDER BY dictkey_count DESC
                     LIMIT 1) AS dictkey_sub
         CROSS JOIN (SELECT field_length, COUNT(*) AS field_length_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE'
                       AND field_length IS NOT NULL
                       AND field_length != ''
                     GROUP BY field_length
                     ORDER BY field_length_count DESC
                     LIMIT 1) AS field_length_sub
         CROSS JOIN (SELECT bde.name AS element_code_name, COUNT(*) AS element_code_count
                     FROM public.base_field_info AS bfi
                              JOIN public.base_data_element AS bde ON bfi.element_code = bde.code
                     WHERE bfi.ename = 'ISP_TYPE'
                       AND bfi.element_code IS NOT NULL
                       AND bfi.element_code != ''
                     GROUP BY element_code_name
                     ORDER BY element_code_count DESC
                     LIMIT 1) AS element_code_sub
         CROSS JOIN (SELECT bdd.name AS determiner_code_name, COUNT(*) AS determiner_code_count
                     FROM public.base_field_info AS bfi
                              JOIN public.base_data_determiner AS bdd ON bfi.determiner_code = bdd.code
                     WHERE bfi.ename = 'ISP_TYPE'
                       AND bfi.determiner_code IS NOT NULL
                       AND bfi.determiner_code != ''
                     GROUP BY determiner_code_name
                     ORDER BY determiner_code_count DESC
                     LIMIT 10) AS determiner_code_sub
         CROSS JOIN (SELECT structure_type, COUNT(*) AS structure_type_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE'
                       AND structure_type IS NOT NULL
                     GROUP BY structure_type
                     ORDER BY structure_type_count DESC
                     LIMIT 1) AS structure_type_sub
         CROSS JOIN (SELECT is_multi_value, COUNT(*) AS is_multi_value_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE'
                       AND is_multi_value IS NOT NULL
                     GROUP BY is_multi_value
                     ORDER BY is_multi_value_count DESC
                     LIMIT 1) AS is_multi_value_sub
         CROSS JOIN (SELECT is_required, COUNT(*) AS is_required_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE'
                       AND is_required IS NOT NULL
                     GROUP BY is_required
                     ORDER BY is_required_count DESC
                     LIMIT 1) AS is_required_sub
         CROSS JOIN (SELECT COUNT(*) AS total_count
                     FROM public.base_field_info
                     WHERE ename = 'ISP_TYPE') AS total_sub;

-- 处理空值情况
SELECT cname_sub.cname                                      AS cname,
       cname_sub.cname_count                                AS cname_count,
       ROUND(COALESCE(cname_sub.cname_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS cname_percentage,
       identifier_sub.identifier                            AS identifier,
       identifier_sub.identifier_count                      AS identifier_count,
       ROUND(COALESCE(identifier_sub.identifier_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS identifier_percentage,
       description_sub.description                          AS description,
       description_sub.description_count                    AS description_count,
       ROUND(COALESCE(description_sub.description_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS description_percentage,
       field_type_sub.field_type_name                       AS field_type_name,
       field_type_sub.field_type_count                      AS field_type_count,
       ROUND(COALESCE(field_type_sub.field_type_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS field_type_percentage,
       dictkey_sub.dictkey                                  AS dictkey,
       dictkey_sub.dictkey_count                            AS dictkey_count,
       ROUND(COALESCE(dictkey_sub.dictkey_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS dictkey_percentage,
       structure_type_sub.structure_type                    AS structure_type,
       COALESCE(structure_type_sub.structure_type_count, 0) AS structure_type_count,
       ROUND(COALESCE(structure_type_sub.structure_type_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS structure_type_percentage,
       field_length_sub.field_length                        AS field_length,
       COALESCE(field_length_sub.field_length_count, 0)     AS field_length_count,
       ROUND(COALESCE(field_length_sub.field_length_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS field_length_percentage,
       element_code_sub.element_code_name                   AS element_code_name,
       COALESCE(element_code_sub.element_code_count, 0)     AS element_code_count,
       ROUND(COALESCE(element_code_sub.element_code_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS element_code_name_percentage,
       determiner_code_sub.determiner_code_name             AS determiner_code_name,
       determiner_code_sub.determiner_code_count            AS determiner_code_count,
       ROUND(COALESCE(determiner_code_sub.determiner_code_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS determiner_code_percentage,
       is_multi_value_sub.is_multi_value                    AS is_multi_value,
       is_multi_value_sub.is_multi_value_count              AS is_multi_value_count,
       ROUND(COALESCE(is_multi_value_sub.is_multi_value_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS is_multi_value_percentage,
       is_required_sub.is_required                          AS is_required,
       is_required_sub.is_required_count                    AS is_required_count,
       ROUND(COALESCE(is_required_sub.is_required_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS is_required_percentage,
       core_flag_sub.core_flag                              AS core_flag,
       core_flag_sub.core_flag_count                        AS core_flag_count,
       ROUND(COALESCE(core_flag_sub.core_flag_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS core_flag_percentage
FROM ((SELECT name AS cname, COUNT(*) AS cname_count
       FROM public.base_field_info
       WHERE (ename = UPPER('field1') OR ename = 'field1')
         AND name ~ '[\u4e00-\u9fa5]'
       GROUP BY name
       ORDER BY cname_count DESC
       LIMIT 1)
      UNION ALL
      (SELECT name AS cname, COUNT(*) AS cname_count
       FROM public.base_field_info
       WHERE (ename = UPPER('field1') OR ename = 'field1')
       GROUP BY name
       ORDER BY cname_count DESC
       LIMIT 1)
      LIMIT 1) AS cname_sub
         CROSS JOIN (SELECT identifier, COUNT(*) AS identifier_count
                     FROM public.base_field_info
                     WHERE (ename = UPPER('field1') OR ename = 'field1')
                     GROUP BY identifier
                     ORDER BY identifier_count DESC
                     LIMIT 1) AS identifier_sub
         CROSS JOIN ((SELECT description, COUNT(*) AS description_count
                      FROM public.base_field_info
                      WHERE (ename = UPPER('field1') OR ename = 'field1')
                        AND description ~ '[\u4e00-\u9fa5]'
                      GROUP BY description
                      ORDER BY description_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT description, COUNT(*) AS description_count
                      FROM public.base_field_info
                      WHERE (ename = UPPER('field1') OR ename = 'field1')
                      GROUP BY description
                      ORDER BY description_count DESC
                      LIMIT 1)
                     LIMIT 1) AS description_sub
         CROSS JOIN (SELECT bft.field_type AS field_type_name, COUNT(*) AS field_type_count
                     FROM public.base_field_info AS bfi
                              JOIN public.base_field_type AS bft ON bfi.field_type = bft.code
                     WHERE (bfi.ename = UPPER('field1') OR bfi.ename = 'field1')
                     GROUP BY bft.field_type
                     ORDER BY field_type_count DESC
                     LIMIT 1) AS field_type_sub
         CROSS JOIN ((SELECT dictkey, COUNT(*) AS dictkey_count
                      FROM public.base_field_info
                      WHERE (ename = UPPER('field1') OR ename = 'field1')
                        AND dictkey IS NOT NULL
                        AND dictkey != ''
                      GROUP BY dictkey
                      ORDER BY dictkey_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS dictkey, 0 AS dictkey_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS dictkey_sub
         CROSS JOIN ((SELECT field_length, COUNT(*) AS field_length_count
                      FROM public.base_field_info
                      WHERE (ename = UPPER('field1') OR ename = 'field1')
                        AND field_length IS NOT NULL
                        AND field_length != ''
                      GROUP BY field_length
                      ORDER BY field_length_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS field_length, 0 AS field_length_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS field_length_sub
         CROSS JOIN ((SELECT bde.name AS element_code_name, COUNT(*) AS element_code_count
                      FROM public.base_field_info AS bfi
                               JOIN public.base_data_element AS bde ON bfi.element_code = bde.code
                      WHERE (bfi.ename = UPPER('field1') OR bfi.ename = 'field1')
                        AND bfi.element_code IS NOT NULL
                        AND bfi.element_code != ''
                      GROUP BY element_code_name
                      ORDER BY element_code_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS element_code_name, 0 AS element_code_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS element_code_sub
         CROSS JOIN ((SELECT bdd.name AS determiner_code_name, COUNT(*) AS determiner_code_count
                      FROM public.base_field_info AS bfi
                               JOIN public.base_data_determiner AS bdd ON bfi.determiner_code = bdd.code
                      WHERE (bfi.ename = UPPER('field1') OR bfi.ename = 'field1')
                        AND bfi.determiner_code IS NOT NULL
                        AND bfi.determiner_code != ''
                      GROUP BY determiner_code_name
                      ORDER BY determiner_code_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS determiner_code_name, 0 AS determiner_code_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS determiner_code_sub
         CROSS JOIN ((SELECT structure_type, COUNT(*) AS structure_type_count
                      FROM public.base_field_info
                      WHERE (ename = UPPER('field1') OR ename = 'field1')
                        AND structure_type IS NOT NULL
                      GROUP BY structure_type
                      ORDER BY structure_type_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS structure_type, 0 AS structure_type_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS structure_type_sub
         CROSS JOIN ((SELECT is_multi_value, COUNT(*) AS is_multi_value_count
                      FROM public.base_field_info
                      WHERE (ename = UPPER('field1') OR ename = 'field1')
                        AND is_multi_value IS NOT NULL
                      GROUP BY is_multi_value
                      ORDER BY is_multi_value_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS is_multi_value, 0 AS is_multi_value_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS is_multi_value_sub
         CROSS JOIN ((SELECT is_required, COUNT(*) AS is_required_count
                      FROM public.base_field_info
                      WHERE (ename = UPPER('field1') OR ename = 'field1')
                        AND is_required IS NOT NULL
                      GROUP BY is_required
                      ORDER BY is_required_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS is_required, 0 AS is_required_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS is_required_sub
         CROSS JOIN (SELECT core_flag, COUNT(*) AS core_flag_count
                     FROM public.base_field_info
                     WHERE (ename = UPPER('field1') OR ename = 'field1')
                     GROUP BY core_flag
                     ORDER BY core_flag_count DESC
                     LIMIT 1) AS core_flag_sub
         CROSS JOIN (SELECT COUNT(*) AS total_count
                     FROM public.base_field_info
                     WHERE (ename = UPPER('field1') OR ename = 'field1')) AS total_sub;


-- 根据字典信息查询字典详情
WITH first_dict AS (SELECT dictkey
                    FROM public.base_field_info
                    WHERE ename = 'DATA_SOURCE'
                      AND dictkey IS NOT NULL
                      AND dictkey != ''
                    GROUP BY dictkey
                    ORDER BY COUNT(*) DESC
                    LIMIT 1)
SELECT id, name, parentname
FROM public.base_dd_tab
WHERE parentid = split_part((SELECT dictkey FROM first_dict), ':', 1)
  AND nlevel = CAST(split_part((SELECT dictkey FROM first_dict), ':', 2) AS INTEGER);


--
WITH first_dict AS (SELECT dictkey
                    FROM public.base_field_info
                    WHERE ename = 'DATA_SOURCE'
                      AND dictkey IS NOT NULL
                      AND dictkey != ''
                    GROUP BY dictkey
                    ORDER BY COUNT(*) DESC
                    LIMIT 1)
SELECT code                                         AS uuid,
       (SELECT dictkey FROM first_dict)             AS dictkey_with_nlevel,
       parentid                                     AS dict_category_code,
       COALESCE(parentname, '无字典类别名称') AS dict_category,
       nlevel                                       AS dict_level,
       id                                           AS dict_id,
       name                                         AS dict_name
FROM public.base_dd_tab
WHERE parentid = split_part((SELECT dictkey FROM first_dict), ':', 1)
  AND nlevel = CAST(split_part((SELECT dictkey FROM first_dict), ':', 2) AS INTEGER);

-- 所有字段
SELECT ename, count(*) ename_count
FROM public.base_field_info
GROUP BY ename
ORDER BY ename_count DESC;