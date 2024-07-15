

#coding=utf-8
import gzip

#with gzip.open(".\\images\\map_2.dat","rb") as f_in:
 #   with open(".\\images\\map_2.txt","wb")as f_out:
  #      f_out.write(f_in.read())

#with open(".\\images\\map_2.txt", "rb") as f_in:
 #   with gzip.open(".\\images\\map_02.dat", "wb") as f_out:
  #      f_out.write(f_in.read())

k = open(".\\images\\map_2.txt", "r", encoding='utf-8', errors='ignore')
k = k.read()
print(k)
