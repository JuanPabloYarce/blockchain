import hashlib
import random
import json

class Bloque:
    def __init__(self, transacciones, hash_previo):
        self.transacciones = transacciones
        self.hash_previo = hash_previo
        self.nonce = None
        self.hash = None
        self.merkle_root = None  


    def calcular_hash_sha256(self, cadena):
        hash_obj = hashlib.sha256()
        hash_obj.update(cadena.encode('utf-8'))
        return hash_obj.hexdigest()

    def calcular_hash_bloque(self):
        merkle_root_str = "" if self.merkle_root is None else self.merkle_root
        bloque_str = json.dumps(self.transacciones) + str(self.nonce) + self.hash_previo + merkle_root_str
        return self.calcular_hash_sha256(bloque_str)

    def realizar_proof_of_work(self, dificultad):
        while True:
            self.nonce = random.randint(1, 1000000)
            self.hash = self.calcular_hash_bloque()
            if self.hash[:dificultad] == '0' * dificultad:
                break

    def calcular_merkle_root(self):
        merkle_tree = [json.dumps(transaccion) for transaccion in self.transacciones]
        self.merkle_root = construir_arbol_merkle(merkle_tree)

    def validar_merkle_root(self):
        merkle_tree = [json.dumps(transaccion) for transaccion in self.transacciones]
        calculada_merkle_root = construir_arbol_merkle(merkle_tree)
        return calculada_merkle_root == self.merkle_root


    def __str__(self):
        return f"Hash Previo: {self.hash_previo}\nNonce: {self.nonce}\nHash del Bloque: {self.hash}\nMerkle Root: {self.merkle_root}\n"


def generar_transacciones(num_transacciones, recompensa_minero=50):
    transacciones = []

    # Transacción de Coinbase
    coinbase_transaccion = {
        'de': 'Sistema',
        'para': 'Minero',  # La recompensa va al minero
        'cantidad': recompensa_minero
    }
    transacciones.append(coinbase_transaccion)

    # Transacciones regulares
    for i in range(1, num_transacciones):
        transaccion = {
            'de': f'Usuario{i}',
            'para': f'Usuario{i+1}',
            'cantidad': random.randint(1, 100)
        }
        transacciones.append(transaccion)

    return transacciones

def construir_arbol_merkle(transacciones):
    if len(transacciones) == 0:
        return None
    if len(transacciones) == 1:
        return transacciones[0]

    nuevos_nodos = []
    for i in range(0, len(transacciones)-1, 2):
        nodo_actual = transacciones[i]
        nodo_siguiente = transacciones[i+1]
        nuevo_nodo = hashlib.sha256((nodo_actual + nodo_siguiente).encode('utf-8')).hexdigest()
        nuevos_nodos.append(nuevo_nodo)

    return construir_arbol_merkle(nuevos_nodos)



def main():
    num_transacciones = 5
    dificultad_proof_of_work = 4
    num_bloques = 3  


    transacciones = generar_transacciones(num_transacciones)

    bloque_genesis = Bloque(transacciones, "0")
    bloque_genesis.realizar_proof_of_work(dificultad_proof_of_work)
    bloque_genesis.calcular_merkle_root()  



    #print("\nMerkle Root:")
    #print(merkle_root)

    print("\nBloque Genesis:")
    print(bloque_genesis)

    bloques = [bloque_genesis]

    for i in range(1, num_bloques):
        nuevas_transacciones = generar_transacciones(num_transacciones)
        nuevo_bloque = Bloque(nuevas_transacciones, bloques[-1].hash)
        nuevo_bloque.calcular_merkle_root()  # Calcular la Merkle Root para el nuevo bloque
        nuevo_bloque.realizar_proof_of_work(dificultad_proof_of_work)


        if nuevo_bloque.validar_merkle_root():
            bloques.append(nuevo_bloque)
            print(f"\nNuevo Bloque ({i}):")
            print(nuevo_bloque)
        else:
            print(f"\nError: El bloque {i} no pasó la validación del árbol de Merkle. No se agrega.")



    print("Transacción de Coinbase:")
    print(transacciones[0])

    # Ejemplo de sumar las recompensas del minero en una cadena de bloques
    total_recompensa_minero = sum([bloque.transacciones[0]['cantidad'] for bloque in bloques])
    print(f"Total de recompensas para el minero: {total_recompensa_minero}")


    # Simulación de manipulación maliciosa de una transacción en un bloque existente
    bloque_modificado = bloques[1]  # Tomamos el segundo bloque como ejemplo
    transaccion_modificada = bloque_modificado.transacciones[1]  # Tomamos la segunda transacción como ejemplo
    transaccion_modificada['cantidad'] = 999  # Modificamos la cantidad de la transacción

    # Verificar integridad del bloque alterado
    nuevo_merkle_root = construir_arbol_merkle([json.dumps(transaccion) for transaccion in bloque_modificado.transacciones])
    print("\nNueva Merkle Root (bloque alterado):", nuevo_merkle_root)

    # Validar la integridad comparando con la Merkle Root original
    if nuevo_merkle_root == bloque_modificado.calcular_hash_sha256(json.dumps(bloque_modificado.transacciones)):
        print("Integridad del bloque preservada.")
    else:
        print("Integridad del bloque violada.")


if __name__ == "__main__":
    main()
