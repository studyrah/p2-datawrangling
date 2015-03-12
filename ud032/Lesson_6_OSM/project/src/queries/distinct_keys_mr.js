mr = db.runCommand({   "mapreduce" : "wwww",   "map" : function() {     for (var key in this) { emit(key, 1); }   },   "reduce" : function(key, values) { return Array.sum(values); },   "out": "wwww" + "_keys" })

cursor = db.wwww_keys.find().sort({"value" : -1}).pretty()
while (cursor.hasNext()) {
  printjson(cursor.next());
}
