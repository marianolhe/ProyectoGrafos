MATCH (u:Usuario {nombre: "Diana"})-[:PREFIERE]->(a:Atributo)<-[:POSEE]-(l:Libro)
MATCH (l)-[l_attr:POSEE]->(a)
MATCH (u)-[u_pref:PREFIERE]->(a)
WITH l, sum(u_pref.intensidad * l_attr.grado) AS puntuacion
ORDER BY puntuacion DESC
LIMIT 5
RETURN l.titulo AS LibroRecomendado, puntuacion