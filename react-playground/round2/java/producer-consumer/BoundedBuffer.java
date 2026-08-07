package com.cisco.iot.concurrency;

import java.util.LinkedList;
import java.util.Queue;

/**
 * The "prove you understand threads" version: a bounded buffer built by hand with
 * synchronized + wait() / notifyAll(). This is what interviewers usually want to see.
 *
 * The three things that MUST be right (and that they'll grill you on):
 *   1. wait() inside a WHILE loop (not if) — re-check the condition after waking.
 *   2. notifyAll() (not notify) — wake all waiters so a producer doesn't only wake
 *      another producer and stall.
 *   3. wait() RELEASES the lock while sleeping, so other threads can make progress
 *      and eventually call notifyAll().
 */
public class BoundedBuffer<T> {

    private final Queue<T> queue = new LinkedList<>();
    private final int capacity;

    public BoundedBuffer(int capacity) {
        this.capacity = capacity;
    }

    public synchronized void put(T item) throws InterruptedException {
        while (queue.size() == capacity) {   // WHILE: the buffer might still be full when we re-wake
            wait();                          // releases the monitor lock; re-acquires it on wake
        }
        queue.add(item);
        notifyAll();                         // signal waiting consumers (and producers)
    }

    public synchronized T take() throws InterruptedException {
        while (queue.isEmpty()) {            // WHILE: another consumer may have drained it before us
            wait();
        }
        T item = queue.remove();
        notifyAll();                         // signal waiting producers (space freed up)
        return item;
    }
}
