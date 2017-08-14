#include<stdio.h>
#include<string.h>   
#include<stdlib.h>  
#include<sys/socket.h>
#include<arpa/inet.h> 
#include<unistd.h>    
#include<pthread.h> // Biblioteca necessária para as threads
#include<time.h> // Biblioteca para capturar data e hora

void *connection_handler(void *); // Protótipo da função de controle das threads
 
int main(int argc , char *argv[])
{
    int socket_desc , client_sock , c , *new_sock;
    struct sockaddr_in server , client;
     
    //Criação do socket
    socket_desc = socket(AF_INET , SOCK_STREAM , 0); // Retorna o descritor do socket
    if (socket_desc == -1)
    {
        printf("Não foi possível criar o socket!");
    }
    puts("Socket criado.");
     
    //Configurando a estrutura do socket
    server.sin_family = AF_INET;
    server.sin_addr.s_addr = INADDR_ANY;
    server.sin_port = htons( 44652 );
     
    //Vinculação do socket com o endereço do servidor
    if( bind(socket_desc,(struct sockaddr *)&server , sizeof(server)) < 0)
    {
        perror("Erro na vinculação de endereço!");
        return 1;
    }
     
    //Escutando o socket
    listen(socket_desc , 3);
        
    //Aguarda e aceita conexões
    puts("Aguardando conexões...");
    c = sizeof(struct sockaddr_in);
    while( (client_sock = accept(socket_desc, (struct sockaddr *)&client, (socklen_t*)&c)) )
    {
        puts("Conexão estabelecida.");
        pthread_t sniffer_thread;
        new_sock = malloc(1);
        *new_sock = client_sock;
         
        if( pthread_create( &sniffer_thread , NULL ,  connection_handler , (void*) new_sock) < 0)
        {
            perror("Não foi possível criar a thread!");
            return 1;
        }
         
    }
     
    if (client_sock < 0)
    {
        perror("Falha na conexão(accept)!");
        return 1;
    }
     
    return 0;
}
 

void *connection_handler(void *socket_desc) // Essa função irá controlar a conexão dos clientes
{
    //Pega o descritor do socket
    int sock = *(int*)socket_desc;
    int read_size;
    time_t mytime; // Variável para armazenar data e hora
    long long int msg_counter = 0;
    char *message , client_message[15];
     

    //Recebe as mensagens do cliente enquanto elas chegarem
    while( (read_size = recv(sock , client_message , 13 , 0)) > 0 )
    {
	
	fflush(stdin);
	mytime = time(NULL);
    printf("Cliente <%d>; Mensagem <%lld>; Conteúdo: %s; Horário de chegada:", sock, msg_counter, client_message);
	fflush(stdin);
	printf(ctime(&mytime));
	msg_counter += 1;
    }
     
    //Se não houverem mais mensagens encerra a conexão.
    if(read_size == 0)
    {
        puts("Cliente desconectado.");
        fflush(stdout);
    }
    else if(read_size == -1)
    {
        perror("Erro na recuperação da mensagem!");
    }
         
    //Libera o socket
    free(socket_desc);
     
    return 0;
}
