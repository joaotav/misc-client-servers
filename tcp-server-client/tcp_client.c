#include<stdio.h> 
#include<string.h>    
#include<sys/socket.h>   
#include<arpa/inet.h>
#include<stdlib.h>
int main(int argc , char *argv[])
{
    int sock;
    struct sockaddr_in server;
    char message[20];
    strcpy(message, "Ola servidor!");
 
    sock = socket(AF_INET , SOCK_STREAM , 0); // socket() retorna o descritor do socket
    if (sock == -1)
    {
        printf("Não foi possível criar o socket.");
    }
    puts("Socket criado.");

    // Configuração do socket
    server.sin_addr.s_addr = inet_addr("127.0.0.1");
    server.sin_family = AF_INET;
    server.sin_port = htons( 44652 );
 
    //Conectando com o servidor
    if (connect(sock , (struct sockaddr *)&server , sizeof(server)) < 0)
    {
        perror("Erro na conexão!");
        return 1;
    }
     
    puts("Conectado.");

    // Mantenha a conexão indefinidamente
    while(1)
    {
        //Envia a mensagem para o servidor
        if( send(sock, message, strlen(message), 0) < 0)  // Retorna o número de bytes enviados se funcionar, senão retorna -1
        {    
            puts("Falha no envio da mensagem!");
            return 1; 
        }   
    }
     
    close(sock);
    return 0;
}
