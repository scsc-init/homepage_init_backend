INSERT INTO key_value (key, value, writing_permission_level)                    
VALUES
  ('president-name', 'XXX', 500),
  ('vice-president-name', 'XXX;XXX', 500),                                                                          
  ('president-phone', '010-XXXX-XXXX',500),                                                      
  ('vice-president-phone', '010-XXXX-XXXX;010-XXXX-XXXX',500)                                                  
ON CONFLICT (key) DO NOTHING;   