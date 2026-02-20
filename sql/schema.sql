-- NoetIA - Database SetUp
    PRAGMA foreign_keys = ON;
-- Catálogos base

CREATE TABLE IF NOT EXISTS perfil (
    idPerfil INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    nombrePerfil TEXT NOT NULL,
    zonaHoraria TEXT NOT NULL,
    horaInicioDia TEXT,
    horaFinDia TEXT,
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS area (
    idArea INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    nombreArea TEXT NOT NULL,
    descripcion TEXT,
    idPerfil INTEGER NOT NULL,
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (idPerfil) REFERENCES perfil(idPerfil)
);

CREATE TABLE IF NOT EXISTS tema (
    idTema INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    idPerfil INTEGER NOT NULL,
    idArea INTEGER NOT NULL,
    nombreTema TEXT NOT NULL,
    descripcionTema TEXT,
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (idPerfil) REFERENCES perfil(idPerfil),
    FOREIGN KEY (idArea) REFERENCES area(idArea)
);

CREATE TABLE IF NOT EXISTS proyecto (
    idProyecto INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    idPerfil INTEGER NOT NULL,
    idArea INTEGER NOT NULL,
    idTema INTEGER NOT NULL,
    nombreProyecto TEXT NOT NULL,
    descripcionProyecto TEXT,
    estadoProyecto TEXT NOT NULL,
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (idPerfil) REFERENCES perfil(idPerfil),
    FOREIGN KEY (idArea) REFERENCES area(idArea),
    FOREIGN KEY (idTema) REFERENCES tema(idTema)
);

-- Pipeline de procesamiento

CREATE TABLE IF NOT EXISTS entradaCruda (
    idEntradaCruda INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    idPerfil INTEGER NOT NULL,
    fuente TEXT NOT NULL,
    contenidoCrudo TEXT NOT NULL,
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (idPerfil) REFERENCES perfil(idPerfil)
);

CREATE TABLE IF NOT EXISTS itemParseado (
    idItemParseado INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL NOT NULL,
    idEntradaCruda INTEGER NOT NULL,
    tipoDetectado TEXT NOT NULL,
    titulo TEXT NOT NULL,
    contenido TEXT NOT NULL,
    fechaDetectada TIMESTAMP,
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP  NOT NULL,

    FOREIGN KEY (idEntradaCruda) REFERENCES entradaCruda(idEntradaCruda)

);

CREATE TABLE IF NOT EXISTS clasificacion (
    idClasificacion INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    idItemParseado INTEGER  NOT NULL UNIQUE,
    idPerfil INTEGER NOT NULL,
    idTema INTEGER,
    tipoFinal TEXT  NOT NULL,
    idArea INTEGER,
    idProyecto INTEGER,
    versionModelo TEXT,
    fechaClasificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY (idItemParseado) REFERENCES itemParseado(idItemParseado),
    FOREIGN KEY (idPerfil) REFERENCES perfil(idPerfil),
    FOREIGN KEY (idArea) REFERENCES area(idArea),
    FOREIGN KEY (idProyecto) REFERENCES proyecto(idProyecto),
    FOREIGN KEY (idTema) REFERENCES tema(idTema)

);

-- Entidades finales

CREATE TABLE IF NOT EXISTS tarea (
    idTarea INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    idClasificacion INTEGER  NOT NULL UNIQUE,
    idPerfil INTEGER NOT NULL,
    idArea INTEGER,
    idProyecto INTEGER,
    idTema INTEGER,
    fechaVencimiento TIMESTAMP,
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP  NOT NULL,
    fechaActualizacion TIMESTAMP,
    estadoTarea TEXT NOT NULL,
    esImportante BOOLEAN NOT NULL,
    esUrgente BOOLEAN NOT NULL,
    cuadranteEisenhower INTEGER NOT NULL,
    minutosEstimados INTEGER,

    FOREIGN KEY(idClasificacion) REFERENCES clasificacion (idClasificacion),
    FOREIGN KEY(idPerfil) REFERENCES perfil(idPerfil),
    FOREIGN KEY(idArea) REFERENCES area(idArea),
    FOREIGN KEY (idProyecto) REFERENCES proyecto(idProyecto),
    FOREIGN KEY (idTema) REFERENCES tema(idTema)
);

CREATE TABLE IF NOT EXISTS nota (
    idNota INTEGER PRIMARY KEY AUTOINCREMENT  NOT NULL,
    idClasificacion  INTEGER NOT NULL UNIQUE,
    idPerfil INTEGER  NOT NULL,
    idArea INTEGER,
    idProyecto INTEGER,
    idTema INTEGER,
    contenidoNota TEXT  NOT NULL,
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP  NOT NULL,

    FOREIGN KEY(idClasificacion) REFERENCES clasificacion (idClasificacion),
    FOREIGN KEY(idPerfil) REFERENCES perfil(idPerfil),
    FOREIGN KEY(idArea) REFERENCES area(idArea),
    FOREIGN KEY (idProyecto) REFERENCES proyecto(idProyecto),
    FOREIGN KEY (idTema) REFERENCES tema(idTema)

);

CREATE TABLE IF NOT EXISTS cita (
    idCita INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    idClasificacion  INTEGER NOT NULL UNIQUE,
    idPerfil INTEGER  NOT NULL,
    idArea INTEGER,
    idProyecto INTEGER,
    idTema INTEGER, 
    tituloCita TEXT NOT NULL,
    descripcionCita TEXT,
    fechaInicio TIMESTAMP NOT NULL,
    fechaFin TIMESTAMP,
    ubicacion TEXT,
    eventoGoogleId TEXT,
    sincronizacionGoogle BOOLEAN DEFAULT FALSE NOT NULL,
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY(idClasificacion) REFERENCES clasificacion (idClasificacion),
    FOREIGN KEY(idPerfil) REFERENCES perfil(idPerfil),
    FOREIGN KEY(idArea) REFERENCES area(idArea),
    FOREIGN KEY (idProyecto) REFERENCES proyecto(idProyecto),
    FOREIGN KEY (idTema) REFERENCES tema(idTema)

);


-- Soporte y metadata

CREATE TABLE IF NOT EXISTS estimacionTiempo (
    idEstimacionTiempo INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    idPerfil INTEGER NOT NULL,
    tipoEtiqueta TEXT,
    minutosPorDefecto INTEGER NOT NULL,
    fechaCreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,

    FOREIGN KEY(idPerfil) REFERENCES perfil(idPerfil)
);
