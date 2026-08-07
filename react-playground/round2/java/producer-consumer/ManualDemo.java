package com.cisco.iot.concurrency;

/**
 * Runs 2 producers + 1 consumer against the hand-rolled BoundedBuffer.
 * 2 producers × 10 items = 20 produced; the consumer takes 20.
 */
public class ManualDemo {
    public static void main(String[] args) {
        BoundedBuffer<Integer> buffer = new BoundedBuffer<>(5);

        Runnable producer = () -> {
            try {
                for (int i = 0; i < 10; i++) {
                    buffer.put(i);
                    System.out.println(Thread.currentThread().getName() + " put " + i);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        Runnable consumer = () -> {
            try {
                for (int i = 0; i < 20; i++) {
                    int x = buffer.take();
                    System.out.println("        C1 consumed " + x);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        new Thread(producer, "P1").start();
        new Thread(producer, "P2").start();
        new Thread(consumer, "C1").start();
    }
}
