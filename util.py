def compare_streams(s1, s2):
  bufsize = 8*1024
  
  while True:
    b1 = s1.read(bufsize)
    b2 = s2.read(bufsize)
    
    if b1 != b2:
      return False
    
    if not b1:
      return True 
