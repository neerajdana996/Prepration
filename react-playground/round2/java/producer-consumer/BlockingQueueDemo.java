package com.cisco.iot.concurrency;

import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;

/**
 * Producer/consumer the PRODUCTION way — a BlockingQueue does the locking + blocking for you.
 *   put(x)  → blocks the producer if the queue is FULL
 *   take()  → blocks the consumer if the queue is EMPTY
 * Zero synchronized / wait / notify in your code.
 */
public class BlockingQueueDemo {
    public static void main(String[] args) throws InterruptedException {
        BlockingQueue<Integer> queue = new ArrayBlockingQueue<>(5); // bounded buffer, capacity 5

        Runnable producer = () -> {
            try {
                for (int i = 1; i <= 10; i++) {
                    queue.put(i);                                   // blocks if full
                    System.out.println("produced " + i + " (size " + queue.size() + ")");
                }
                queue.put(-1);                                      // poison pill → stop consumer
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();                 // restore the interrupt flag
            }
        };

        Runnable consumer = () -> {
            try {
                while (true) {
                    int x = queue.take();                           // blocks if empty
                    if (x == -1) break;                             // poison pill
                    System.out.println("            consumed " + x);
                    Thread.sleep(50);                               // simulate a slower consumer
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        Thread p = new Thread(producer), c = new Thread(consumer);
        p.start(); c.start();
        p.join(); c.join();
    }
}
