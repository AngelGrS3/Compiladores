# by: Tristan perez and Angel Garcia

import sys
# CONSTANTES Y TABLAS

TABLA_AFD = {
    # estado inicial
    ("q0", "M"): "M",
    ("q0", "A"): "A",
    ("q0", "S"): "S",
    ("q0", "E"): "E",

    # MOV R, d
    ("M", "O"): "MO",
    ("MO", "V"): "MOV",
    ("MOV", "ESPACIO"): "MOV_SP",
    ("MOV_SP", "ESPACIO"): "MOV_SP",
    ("MOV_SP", "A"): "MOV_A",
    ("MOV_SP", "B"): "MOV_B",
    ("MOV_A", "L"): "MOV_REG",
    ("MOV_B", "L"): "MOV_REG",
    ("MOV_REG", "COMA"): "MOV_COMA",
    ("MOV_REG", "ESPACIO"): "MOV_REG_SP",
    ("MOV_REG_SP", "ESPACIO"): "MOV_REG_SP",
    ("MOV_REG_SP", "COMA"): "MOV_COMA",
    ("MOV_COMA", "ESPACIO"): "MOV_COMA",
    ("MOV_COMA", "DIGITO"): "MOV_NUM",
    ("MOV_NUM", "DIGITO"): "MOV_NUM",

    # ADD AL, BL
    ("A", "D"): "AD",
    ("AD", "D"): "ADD",
    ("ADD", "ESPACIO"): "ADD_SP",
    ("ADD_SP", "ESPACIO"): "ADD_SP",
    ("ADD_SP", "A"): "ADD_A",
    ("ADD_A", "L"): "ADD_AL",
    ("ADD_AL", "COMA"): "ADD_COMA",
    ("ADD_AL", "ESPACIO"): "ADD_AL_SP",
    ("ADD_AL_SP", "ESPACIO"): "ADD_AL_SP",
    ("ADD_AL_SP", "COMA"): "ADD_COMA",
    ("ADD_COMA", "ESPACIO"): "ADD_COMA",
    ("ADD_COMA", "B"): "ADD_B",
    ("ADD_B", "L"): "ADD_BL",

    # STO d
    ("S", "T"): "ST",
    ("ST", "O"): "STO",
    ("STO", "ESPACIO"): "STO_SP",
    ("STO_SP", "ESPACIO"): "STO_SP",
    ("STO_SP", "DIGITO"): "STO_NUM",
    ("STO_NUM", "DIGITO"): "STO_NUM",

    # END
    ("E", "N"): "EN",
    ("EN", "D"): "END",
}

ESTADO_INICIAL = "q0"
ESTADOS_ACEPTACION = {"MOV_NUM", "ADD_BL", "STO_NUM", "END"}

# Token que se emite al llegar a un estado
TOKEN_AL_LLEGAR = {
    "MOV": "MOV",
    "ADD": "ADD",
    "STO": "STO",
    "END": "END",
    "MOV_REG": "REGISTRO",
    "ADD_AL": "REGISTRO",
    "ADD_BL": "REGISTRO",
    "MOV_COMA": "COMA",
    "ADD_COMA": "COMA",
    "MOV_NUM": "NUMERO",
    "STO_NUM": "NUMERO",
}

# Mensaje de error segun el estado donde se quedo el AFD
MENSAJES_ERROR = {
    "q0": "mnemonico no reconocido (se esperaba MOV, ADD, STO o END).",
    "M": "mnemonico no reconocido.",
    "MO": "mnemonico no reconocido.",
    "A": "mnemonico no reconocido.",
    "AD": "mnemonico no reconocido.",
    "S": "mnemonico no reconocido.",
    "ST": "mnemonico no reconocido.",
    "E": "mnemonico no reconocido.",
    "EN": "mnemonico no reconocido.",

    "MOV": "despues de MOV se esperaba un espacio y sus operandos.",
    "MOV_SP": "registro invalido: MOV solo admite AL o BL como registro destino.",
    "MOV_A": "registro invalido: MOV solo admite AL o BL como registro destino.",
    "MOV_B": "registro invalido: MOV solo admite AL o BL como registro destino.",
    "MOV_REG": "falta la coma entre el registro y la direccion.",
    "MOV_REG_SP": "falta la coma entre el registro y la direccion.",
    "MOV_COMA": "se esperaba una direccion decimal despues de la coma.",
    "MOV_NUM": "sobran operandos despues de la direccion.",

    "ADD": "despues de ADD se esperaba un espacio y sus operandos.",
    "ADD_SP": "ADD requiere AL como primer registro.",
    "ADD_A": "ADD requiere AL como primer registro.",
    "ADD_AL": "falta la coma entre AL y BL.",
    "ADD_AL_SP": "falta la coma entre AL y BL.",
    "ADD_COMA": "falta el segundo registro BL despues de la coma.",
    "ADD_B": "ADD requiere BL como segundo registro.",
    "ADD_BL": "sobran operandos despues de BL.",

    "STO": "STO requiere un espacio y una direccion decimal no negativa.",
    "STO_SP": "STO requiere una direccion decimal no negativa.",
    "STO_NUM": "sobran operandos despues de la direccion.",

    "END": "END no admite operandos.",
}

#AFD

class AFD:
    def __init__(self):
        self.tabla = TABLA_AFD
        self.inicial = ESTADO_INICIAL
        self.aceptacion = ESTADOS_ACEPTACION

    def categoria(self, c):
        # convierte el caracter en la categoria que usa la tabla
        if c in "0123456789":
            return "DIGITO"
        if c in " \t":
            return "ESPACIO"
        if c == ",":
            return "COMA"
        return c

    def validar(self, texto):
        # regresa (valido, tokens, mensaje_error)
        estado = self.inicial
        tokens = []      # lista de [tipo, lexema]
        buffer = ""      # caracteres del lexema que se esta armando

        for c in texto:
            cat = self.categoria(c)
            clave = (estado, cat)

            if clave not in self.tabla:
                return False, [], MENSAJES_ERROR.get(estado, "entrada invalida.")

            anterior = estado
            estado = self.tabla[clave]

            # los espacios no forman parte de ningun lexema
            if cat != "ESPACIO":
                buffer += c

            if estado in TOKEN_AL_LLEGAR:
                tipo = TOKEN_AL_LLEGAR[estado]
                if estado != anterior:
                    # lexema nuevo
                    tokens.append([tipo, buffer])
                    buffer = ""
                elif tipo == "NUMERO":
                    # otro digito del mismo numero
                    tokens[-1][1] += buffer
                    buffer = ""

        # al terminar la entrada hay que estar en un estado de aceptacion
        if estado not in self.aceptacion:
            return False, [], MENSAJES_ERROR.get(estado, "la instruccion esta incompleta.")

        return True, tokens, ""


# objeto instruccion

class Instruccion:
    def __init__(self, operacion, registros, direccion):
        self.operacion = operacion
        self.registros = registros
        self.direccion = direccion

    def __str__(self):
        regs = "[" + ", ".join('"' + r + '"' for r in self.registros) + "]"
        return ("{\n"
                f'operacion: "{self.operacion}",\n'
                f"registros: {regs},\n"
                f"direccion: {self.direccion}\n"
                "}")

#contruir el objeto a partir de tokens

def construir_instruccion(tokens):
    operacion = tokens[0][1]
    registros = [lex for tipo, lex in tokens if tipo == "REGISTRO"]
    direccion = None
    for tipo, lex in tokens:
        if tipo == "NUMERO":
            direccion = int(lex)
    return Instruccion(operacion, registros, direccion)



#  maquina de moore

# Para cada operacion: estado -> (salida, siguiente estado)
# {reg} y {dir} se sustituyen con los datos del objeto
RUTAS = {
    "MOV": {
        "Preparar direccion": ("MAR ← {dir}", "Leer memoria"),
        "Leer memoria": ("MBR ← M[MAR]", "Cargar registro"),
        "Cargar registro": ("{reg} ← MBR", "Fin"),
        "Fin": (None, None),
    },
    "ADD": {
        "Sumar": ("ACC ← AL + BL", "Fin"),
        "Fin": (None, None),
    },
    "STO": {
        "Preparar direccion": ("MAR ← {dir}", "Copiar ACC"),
        "Copiar ACC": ("MBR ← ACC", "Escribir memoria"),
        "Escribir memoria": ("M[MAR] ← MBR", "Fin"),
        "Fin": (None, None),
    },
    "END": {
        "Detener": ("HALT ← 1", "Fin"),
        "Fin": (None, None),
    },
}

ESTADO_INICIAL_MOORE = {
    "MOV": "Preparar direccion",
    "ADD": "Sumar",
    "STO": "Preparar direccion",
    "END": "Detener",
}


class MaquinaMoore:
    def __init__(self, instruccion):
        # solo usa el objeto, no vuelve a leer el texto
        self.instruccion = instruccion
        self.rutas = RUTAS[instruccion.operacion]
        self.estado = ESTADO_INICIAL_MOORE[instruccion.operacion]

    def terminado(self):
        return self.estado == "Fin"

    def siguientePaso(self):
        # emite la salida del estado actual y avanza al siguiente
        plantilla, siguiente = self.rutas[self.estado]
        salida = None
        if plantilla is not None:
            reg = self.instruccion.registros[0] if self.instruccion.registros else ""
            salida = plantilla.format(reg=reg, dir=self.instruccion.direccion)
        if siguiente is not None:
            self.estado = siguiente
        return salida



#procesar instruccion


def procesar(texto):
    print("ENTRADA")
    print(texto)
    print("VALIDACION MEDIANTE AFD")

    afd = AFD()
    valido, tokens, error = afd.validar(texto)

    if not valido:
        print("Instruccion invalida: " + error)
        print("No se construye el objeto instruccion.")
        print("No se generan microoperaciones.")
        return

    print("Instruccion valida.")

    print("TOKENS RECONOCIDOS")
    for tipo, lexema in tokens:
        print(f'{tipo}("{lexema}")')

    instr = construir_instruccion(tokens)

    print("COMPONENTES IDENTIFICADOS")
    print("Mnemonico: " + instr.operacion)
    if instr.operacion == "MOV":
        print("Registro destino: " + instr.registros[0])
    elif instr.operacion == "ADD":
        print("Registros: " + ", ".join(instr.registros))
    if instr.direccion is not None:
        print(f"Direccion de memoria: {instr.direccion}")
        print("Direccionamiento: directo")

    print("OBJETO INSTRUCCION")
    print(instr)

    print("MICROOPERACIONES GENERADAS POR MOORE")
    moore = MaquinaMoore(instr)
    numero = 1
    while not moore.terminado():
        salida = moore.siguientePaso()
        if salida is not None:
            print(f"{numero}. {salida}")
            numero += 1
    print("Generacion terminada.")


# casos de prueba automatizados

VALIDAS = ["MOV AL, 6", "MOV BL, 7", "ADD AL, BL", "STO 8", "END"]
INVALIDAS = ["MOV AX, 6", "MOV AL 6", "ADD AL,", "STO", "END 8"]


def correr_pruebas():
    print("\nENTRADAS VALIDAS ")
    for texto in VALIDAS:
        print("\n" + "-" * 40)
        procesar(texto)

    print("\nENTRADAS INVALIDAS")
    for texto in INVALIDAS:
        print("\n" + "-" * 40)
        procesar(texto)


def main():
    while True:
        
        print("\n     MENU")
        print("1. Escribir una instruccion")
        print("2. Correr los casos de prueba")
        print("3. Salir")
        opcion = input("Opcion: ").strip()

        if opcion == "1":
            texto = input("Instruccion: ").strip()
            print()
            procesar(texto)
        elif opcion == "2":
            correr_pruebas()
        elif opcion == "3":
            print("Hasta luego.")
            break
        else:
            print("Opcion no valida.")


if __name__ == "__main__":
    main()
