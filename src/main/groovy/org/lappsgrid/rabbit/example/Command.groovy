package org.lappsgrid.rabbit.example

import org.lappsgrid.rabbitmq.Message
import org.lappsgrid.rabbitmq.RabbitMQ
import org.lappsgrid.rabbitmq.topic.*
import org.lappsgrid.serialization.Serializer

import java.util.concurrent.CountDownLatch

class Command {

    static void main(String[] args) {
        String host = "localhost"
        String username = "guest"
        String password = "guest"
        if (args.length == 3) {
            host = args[0]
            username = args[1]
            password = args[2]
        }
        RabbitMQ.configure(host, username, password)
        CountDownLatch latch = null

        MessageBox inbox = new MessageBox("askme", "groovy_queue") {
            @Override
            void recv(Message message) {
                println Serializer.toPrettyJson(message)
                latch.countDown()
            }
        }

        PostOffice po = new PostOffice("askme")
        println "Type EXIT to terminate the program."
        Scanner stdin = new Scanner(System.in)
        boolean running = true
        while (running) {
            print "\$> "
            String command = stdin.nextLine()
            if (command == "exit" || command == "EXIT") {
                running = false
            }
            else if (command == "halt" || command == "HALT") {
                Message message = new Message("HALT", "HALT", "python_queue")
                po.send(message)
            }
            else {
                String[] parts = command.split(" ")
                String payload = parts.length > 1 ? parts[1..-1].join(" ") : ""
                Message message = new Message(parts[0], payload, "python_queue", "groovy_queue")
                latch = new CountDownLatch(1)
                po.send(message)
                latch.await()
                latch = null
            }
        }
        inbox.close()
        po.close()
        println "Done."
    }
}


