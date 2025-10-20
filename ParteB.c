
// Librerías estándar de C para entrada/salida, manejo de memoria y cadenas
#include <stdio.h>      // Para printf, fopen, fgets, etc.
#include <stdlib.h>     // Para malloc, free
#include <string.h>     // Para manejo de cadenas (strcpy, strcmp, etc.)
#include <math.h>       // Para funciones matemáticas (sqrt, pow)
#include <windows.h>    // Para SetConsoleOutputCP (permite mostrar caracteres especiales en consola de Windows)


// Estructura para almacenar una lectura de temperatura
struct Lectura {
    char fecha[11];        // Fecha de la lectura (formato: DD/MM/YYYY)
    char hora[9];          // Hora de la lectura (formato: HH:MM:SS)
    float temperatura;     // Valor de la temperatura
    char tendencia[10];    // Tendencia de la temperatura 
};


// Nodo de la lista enlazada para almacenar lecturas
struct nodo {
    struct Lectura dato;   // Dato de tipo Lectura
    struct nodo *sig;      // Puntero al siguiente nodo
};


// Función para reservar memoria dinámica para un nuevo nodo
struct nodo *creanodo(void) {
    // malloc reserva memoria equivalente al tamaño de un nodo
    return (struct nodo *) malloc(sizeof(struct nodo));
}


// Función para leer el archivo de registro y crear una lista enlazada de lecturas
struct nodo *ListaRegistros(FILE *registro){
    char linea[100];
    struct nodo *anterior = NULL; // Puntero al nodo anterior (para formar la lista)

    // Lee cada línea del archivo hasta el final
    while (fgets(linea, sizeof(linea), registro)!= NULL) {
        struct nodo *nuevo;             // Puntero al nuevo nodo
        nuevo = creanodo();             // Reserva memoria para el nuevo nodo
        struct Lectura lectura;         // Estructura para almacenar los datos de la lectura

        // Extrae los datos de la línea y los guarda en la estructura lectura
        sscanf(linea, "Fecha: %10s; Hora: %8s; Temperatura: %f; Tendencia: %9s", 
               lectura.fecha, lectura.hora, &lectura.temperatura, lectura.tendencia);

        nuevo->dato=lectura;            // Copia los datos en el nuevo nodo
        nuevo->sig = anterior;          // Apunta al nodo anterior para formar la lista
        anterior = nuevo;               // Actualiza el anterior
    }
    return anterior; // Devuelve el primer nodo de la lista 
}


// Función para contar la cantidad de registros (nodos) en la lista
int CantidadRegistros(struct nodo *ListaRegistros){
    struct nodo *p = ListaRegistros; // Puntero auxiliar para recorrer la lista
    int cantidad = 0;
    while (p != NULL) {
        p = p->sig;                 // Avanza al siguiente nodo
        cantidad++;                 // Incrementa la cantidad
    }
    return cantidad;                // Devuelve la cantidad de nodos
}


// Función para encontrar el nodo con la temperatura máxima
struct nodo *TemperaturaMaxima(struct nodo *ListaRegistros){
    struct nodo *p = ListaRegistros;
    struct nodo *maximo = p;         // Inicializa el máximo con el primer nodo
    while (p !=NULL){
        if(p->dato.temperatura > maximo->dato.temperatura){
            maximo = p;        // Actualiza el máximo si se encuentra una temperatura mayor
        }
        p = p->sig;            // Avanza al siguiente nodo
    }
    return maximo;             // Devuelve el nodo con la temperatura máxima
}


// Función para encontrar el nodo con la temperatura mínima
struct nodo *TemperaturaMinima(struct nodo *ListaRegistros){ 
    struct nodo *p = ListaRegistros;
    struct nodo *minimo = p;      // Inicializa el mínimo con el primer nodo
    while (p !=NULL){
        if(p->dato.temperatura < minimo->dato.temperatura){
            minimo = p;        // Actualiza el mínimo si se encuentra una temperatura menor
        }
        p = p->sig;            // Avanza al siguiente nodo
    }
    return minimo;             // Devuelve el nodo con la temperatura mínima
}


// Función para buscar el nodo anterior donde insertar (para ordenar por temperatura)
struct nodo *searchAnteriorTemperatura(struct nodo *inicio, struct nodo *nuevo) {
    struct nodo *p = inicio;
    struct nodo *anterior = NULL;   // Devuelve NULL si debe insertarse al inicio

    // Recorre la lista hasta encontrar el nodo con temperatura mayor al nuevo
    while (p != NULL) {
        if (p->dato.temperatura > nuevo->dato.temperatura) {
            return anterior;   // Encontramos dónde insertar
        }
        anterior = p;          // Avanzamos
        p = p->sig;
    }
    return anterior;           // Si llega al final, se inserta al final de la lista
}


// Función para ordenar una lista enlazada por temperatura (de menor a mayor)
struct nodo *ordenarLista(struct nodo *lista) {
    struct nodo *listaOrdenada = NULL;            // Lista nueva ordenada
    struct nodo *actual = lista;                  // Nodo a insertar

    while (actual != NULL) {
        struct nodo *siguiente = actual->sig;     // Guardamos el nodo siguiente de la lista original
        struct nodo *anterior = searchAnteriorTemperatura(listaOrdenada, actual); // Buscamos dónde insertar el nodo en la lista ordenada

        if (anterior == NULL) {    // Si no hay nodo anterior lo inserta al inicio
            actual->sig = listaOrdenada;
            listaOrdenada = actual;

        } else {                   // Si hay nodo anterior lo inserta después del nodo anterior
            actual->sig = anterior->sig;
            anterior->sig = actual;
        }
        actual = siguiente;        // Pasamos al siguiente nodo de la lista original
    }
    return listaOrdenada;          // Devolvemos la lista ya ordenada
}
   

// Función para calcular la temperatura media (promedio)
float TemperaturaMedia(struct nodo *lista, int cantidad){
    struct nodo *p = lista;
    float suma = 0;
    while (p != NULL){
        suma = suma + p->dato.temperatura;  // Suma todas las temperaturas
        p = p->sig;
    }
    float media = suma / cantidad;          // Calcula el promedio (la media)
    return media;
}


// Función para calcular la temperatura mediana
float TemperaturaMediana(struct nodo *lista, int cantidad){
    struct nodo *p1 = lista;
    struct nodo *p2 = lista;
    float mediana = 0;

    if (cantidad %2 == 0){  // Si la cantidad es par
       int ubicacionMediana1 = cantidad / 2;
       int ubicacionMediana2 = (cantidad + 2)/2;
       // Avanza hasta la primera posición de la mediana
       for (int i = 1; i < ubicacionMediana1; i++){
            p1 = p1->sig;
        } 
       // Avanza hasta la segunda posición de la mediana
       for (int i = 1; i < ubicacionMediana2; i++){
            p2 = p2->sig;
        } 
        // Calcula el promedio de las dos posiciones centrales
        mediana = (p1->dato.temperatura + p2->dato.temperatura) / 2;
    }
    else{   // Si la cantidad es impar
        int ubicacionMediana = (cantidad + 1) / 2; //Posición central
        for (int i = 1; i <ubicacionMediana; i++){
            p1 = p1->sig;
        } 
        mediana = p1->dato.temperatura; // La mediana es la temperatura de la ubicación central
    }
    return mediana;
}



// Función para calcular la temperatura moda 
float TemperaturaModa(struct nodo *lista) {
    struct nodo *p1, *p2;
    float moda = 0;           // Temperatura que más se repite
    int maxRepeticiones = 0;  // Número de veces que se repite la moda
    int hayEmpate = 0;        // Para detectar si hay empate entre dos o más temperaturas

    p1 = lista;
    while (p1 != NULL) {     // Recorre cada nodo de la lista
        int contador = 1;    // Al menos aparece 1 vez 
        p2 = p1->sig;        // Compara con los siguientes nodos

        while (p2 != NULL) {
            if (p2->dato.temperatura == p1->dato.temperatura) {
                contador++;  // Encontró otra vez la misma temperatura
            }
            p2 = p2->sig;
        }

        // Si esta temperatura tiene más repeticiones que la anterior, la guardamos como moda
        if (contador > maxRepeticiones) {
            maxRepeticiones = contador;
            moda = p1->dato.temperatura;
            hayEmpate = 0;
        }
        // Si hay otra temperatura con la misma frecuencia máxima
        else if(contador == maxRepeticiones && p1->dato.temperatura!= moda){
            hayEmpate=1;
        }
        p1 = p1->sig; // Pasamos al siguiente nodo
    }
    if (hayEmpate==1){
        moda=0; // Si hay empate, no hay moda
    }
    return moda;
}


// Función para calcular la desviación estándar de las temperaturas
float DesviacionEstandar(struct nodo *lista, int cantidad, float media){
    struct nodo *p = lista;
    float suma = 0;
    while (p != NULL){
        suma = suma + pow(p->dato.temperatura - media, 2); // Suma de las diferencias al cuadrado
        p = p->sig;
    }
    float varianza = suma / cantidad;   // Calcula la varianza
    float desviacion = sqrt(varianza);  // Calcula la desviación estándar
    return desviacion; 
}


int main(){
    SetConsoleOutputCP(CP_UTF8); // Permite mostrar caracteres especiales en la consola de Windows

    // 1. Abrir el archivo de registro en modo lectura
    FILE *registro = fopen("registro.txt", "r");
    if (registro == NULL) {
        printf("No se pudo abrir el archivo.\n");
        return 1; // Termina el programa si no se puede abrir el archivo
    }

    // 2. Leer todas las lecturas del archivo y guardarlas en una lista enlazada
    struct nodo *lista = ListaRegistros(registro);
    fclose(registro); // Cierra el archivo

    // 3. Contar cuántas lecturas hay en la lista
    int cantidad = CantidadRegistros(lista);
    
    if (cantidad == 0) {
        printf("No hay lecturas para analizar.\n");
        return 0; // Termina si no hay lecturas
    }
    else{
        printf("Cantidad de lecturas: %d\n", cantidad);
    }

    // 4. Ordenar la lista por temperatura (de menor a mayor)
    lista = ordenarLista(lista);

    // 5. Mostrar temperatura mínima y máxima
    struct nodo *min = TemperaturaMinima(lista);
    struct nodo *max = TemperaturaMaxima(lista);
    printf("Temperatura mínima: %.2f°C (Fecha: %s, Hora: %s)\n", min->dato.temperatura, min->dato.fecha, min->dato.hora);
    printf("Temperatura máxima: %.2f°C (Fecha: %s, Hora: %s)\n", max->dato.temperatura, max->dato.fecha, max->dato.hora);

    // 6. Calcular y mostrar la media
    float media = TemperaturaMedia(lista, cantidad);
    printf("Media: %.2f°C\n", media);

    // 7. Calcular y mostrar la mediana
    float mediana = TemperaturaMediana(lista, cantidad);
    printf("Mediana: %.2f°C\n", mediana);

    // 8. Calcular y mostrar la moda
    float moda = TemperaturaModa(lista);
    if (moda == 0){
        printf("Moda: No hay moda definida (todas las temperaturas son únicas o hay empate)\n");
    }
    else{
    printf("Moda: %.2f°C\n", moda);
    }

    // 9. Calcular y mostrar la desviación estándar
    float desviacion = DesviacionEstandar(lista, cantidad, media);
    printf("Desviación estándar: %.2f°C\n", desviacion);
    // Para las lecturas de temperatura, la desviación estándar es más adecuada porque:
    // la unidad es la misma que la de los datos, lo que facilita la interpretación

    // 10. Liberar memoria de la lista enlazada
    while (lista != NULL) {
      struct nodo *p = lista;
       lista = lista->sig;
       free(p);   // Libera la memoria de cada nodo
    }

    return 0; // Fin del programa
}

