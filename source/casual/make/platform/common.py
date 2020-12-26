import casual.make.target as target

def add_item_to_list( items, item):
   new_list = []
   if not items:
      return new_list
      
   for i in items:
      if isinstance( i, target.Target):
         new_list.append( item + i.name)
      else:
         new_list.append( item + i)
   return new_list