INSERT INTO key_value (key, value, writing_permission_level)                    
VALUES
  ('president-name', '강명석', 500),
  ('vice-president-name', '박상혁;박성현', 500),                                                                          
  ('president-phone', '010-2058-7356',500),                                                      
  ('vice-president-phone', '010-4014-1871;010-3537-2998',500)                                                  
ON CONFLICT (key) DO NOTHING;   