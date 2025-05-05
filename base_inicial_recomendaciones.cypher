// Crear usuarios
CREATE (:Usuario {nombre: "Diana"});
CREATE (:Usuario {nombre: "Lucas"});
CREATE (:Usuario {nombre: "María"});
CREATE (:Usuario {nombre: "Andrés"});
CREATE (:Usuario {nombre: "Sofía"});

// Crear libros
CREATE (:Libro {titulo: "Gone Girl"});
CREATE (:Libro {titulo: "1984"});
CREATE (:Libro {titulo: "El Nombre del Viento"});
CREATE (:Libro {titulo: "Reina Roja"});
CREATE (:Libro {titulo: "Cien Años de Soledad"});

// Crear atributos narrativos
CREATE (:Atributo {tipo: "ritmo_rápido"});
CREATE (:Atributo {tipo: "ritmo_lento"});
CREATE (:Atributo {tipo: "giros_inesperados"});
CREATE (:Atributo {tipo: "desarrollo_personajes"});
CREATE (:Atributo {tipo: "prosa_concisa"});
CREATE (:Atributo {tipo: "descriptivo"});

// Relacionar usuarios con atributos
MATCH (u:Usuario {nombre: "Diana"}), (a:Atributo {tipo: "ritmo_rápido"}) CREATE (u)-[:PREFIERE {intensidad: 0.8}]->(a);
MATCH (u:Usuario {nombre: "Diana"}), (a:Atributo {tipo: "giros_inesperados"}) CREATE (u)-[:PREFIERE {intensidad: 0.9}]->(a);
MATCH (u:Usuario {nombre: "Diana"}), (a:Atributo {tipo: "prosa_concisa"}) CREATE (u)-[:PREFIERE {intensidad: 0.7}]->(a);

MATCH (u:Usuario {nombre: "Lucas"}), (a:Atributo {tipo: "ritmo_lento"}) CREATE (u)-[:PREFIERE {intensidad: 0.4}]->(a);
MATCH (u:Usuario {nombre: "Lucas"}), (a:Atributo {tipo: "desarrollo_personajes"}) CREATE (u)-[:PREFIERE {intensidad: 0.8}]->(a);
MATCH (u:Usuario {nombre: "Lucas"}), (a:Atributo {tipo: "descriptivo"}) CREATE (u)-[:PREFIERE {intensidad: 0.6}]->(a);

MATCH (u:Usuario {nombre: "María"}), (a:Atributo {tipo: "ritmo_rápido"}) CREATE (u)-[:PREFIERE {intensidad: 0.9}]->(a);
MATCH (u:Usuario {nombre: "María"}), (a:Atributo {tipo: "giros_inesperados"}) CREATE (u)-[:PREFIERE {intensidad: 0.6}]->(a);
MATCH (u:Usuario {nombre: "María"}), (a:Atributo {tipo: "prosa_concisa"}) CREATE (u)-[:PREFIERE {intensidad: 0.9}]->(a);

MATCH (u:Usuario {nombre: "Andrés"}), (a:Atributo {tipo: "ritmo_lento"}) CREATE (u)-[:PREFIERE {intensidad: 0.5}]->(a);
MATCH (u:Usuario {nombre: "Andrés"}), (a:Atributo {tipo: "giros_inesperados"}) CREATE (u)-[:PREFIERE {intensidad: 0.3}]->(a);
MATCH (u:Usuario {nombre: "Andrés"}), (a:Atributo {tipo: "descriptivo"}) CREATE (u)-[:PREFIERE {intensidad: 0.7}]->(a);

MATCH (u:Usuario {nombre: "Sofía"}), (a:Atributo {tipo: "desarrollo_personajes"}) CREATE (u)-[:PREFIERE {intensidad: 0.9}]->(a);
MATCH (u:Usuario {nombre: "Sofía"}), (a:Atributo {tipo: "descriptivo"}) CREATE (u)-[:PREFIERE {intensidad: 0.4}]->(a);
MATCH (u:Usuario {nombre: "Sofía"}), (a:Atributo {tipo: "prosa_concisa"}) CREATE (u)-[:PREFIERE {intensidad: 0.5}]->(a);

// Relacionar libros con atributos
MATCH (l:Libro {titulo: "Gone Girl"}), (a:Atributo {tipo: "ritmo_rápido"}) CREATE (l)-[:POSEE {grado: 0.85}]->(a);
MATCH (l:Libro {titulo: "Gone Girl"}), (a:Atributo {tipo: "giros_inesperados"}) CREATE (l)-[:POSEE {grado: 0.9}]->(a);
MATCH (l:Libro {titulo: "Gone Girl"}), (a:Atributo {tipo: "prosa_concisa"}) CREATE (l)-[:POSEE {grado: 0.7}]->(a);

MATCH (l:Libro {titulo: "1984"}), (a:Atributo {tipo: "ritmo_lento"}) CREATE (l)-[:POSEE {grado: 0.6}]->(a);
MATCH (l:Libro {titulo: "1984"}), (a:Atributo {tipo: "giros_inesperados"}) CREATE (l)-[:POSEE {grado: 0.4}]->(a);
MATCH (l:Libro {titulo: "1984"}), (a:Atributo {tipo: "desarrollo_personajes"}) CREATE (l)-[:POSEE {grado: 0.8}]->(a);
MATCH (l:Libro {titulo: "1984"}), (a:Atributo {tipo: "descriptivo"}) CREATE (l)-[:POSEE {grado: 0.7}]->(a);

MATCH (l:Libro {titulo: "El Nombre del Viento"}), (a:Atributo {tipo: "ritmo_lento"}) CREATE (l)-[:POSEE {grado: 0.5}]->(a);
MATCH (l:Libro {titulo: "El Nombre del Viento"}), (a:Atributo {tipo: "desarrollo_personajes"}) CREATE (l)-[:POSEE {grado: 0.9}]->(a);
MATCH (l:Libro {titulo: "El Nombre del Viento"}), (a:Atributo {tipo: "descriptivo"}) CREATE (l)-[:POSEE {grado: 0.9}]->(a);

MATCH (l:Libro {titulo: "Reina Roja"}), (a:Atributo {tipo: "ritmo_rápido"}) CREATE (l)-[:POSEE {grado: 0.9}]->(a);
MATCH (l:Libro {titulo: "Reina Roja"}), (a:Atributo {tipo: "giros_inesperados"}) CREATE (l)-[:POSEE {grado: 0.85}]->(a);
MATCH (l:Libro {titulo: "Reina Roja"}), (a:Atributo {tipo: "prosa_concisa"}) CREATE (l)-[:POSEE {grado: 0.8}]->(a);

MATCH (l:Libro {titulo: "Cien Años de Soledad"}), (a:Atributo {tipo: "ritmo_lento"}) CREATE (l)-[:POSEE {grado: 0.3}]->(a);
MATCH (l:Libro {titulo: "Cien Años de Soledad"}), (a:Atributo {tipo: "desarrollo_personajes"}) CREATE (l)-[:POSEE {grado: 0.95}]->(a);
MATCH (l:Libro {titulo: "Cien Años de Soledad"}), (a:Atributo {tipo: "descriptivo"}) CREATE (l)-[:POSEE {grado: 0.95}]->(a);
