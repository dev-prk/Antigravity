import java.io.*;
import java.util.*;

public class Main {
    static class Node {
        int data;
        Node next;
        Node(int data) { this.data = data; }
    }

    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        String nLine = br.readLine();
        if (nLine == null || nLine.isEmpty()) return;
        int n = Integer.parseInt(nLine.trim());
        if (n == 0) { System.out.println(-1); return; }
        
        String valsLine = br.readLine();
        if (valsLine == null || valsLine.isEmpty()) { System.out.println(-1); return; }
        
        String[] tokens = valsLine.trim().split("\\s+");
        Node head = null, tail = null;
        for (String t : tokens) {
            int val = Integer.parseInt(t);
            Node nd = new Node(val);
            if (head == null) head = tail = nd;
            else { tail.next = nd; tail = nd; }
        }

        head = bucketSort(head, n);

        StringBuilder sb = new StringBuilder();
        Node cur = head;
        int cnt = 0;
        while (cur != null) {
            if (cnt > 0) sb.append(' ');
            sb.append(cur.data);
            cur = cur.next;
            cnt++;
        }
        if (cnt == 0) System.out.println(-1);
        else System.out.println(sb.toString());
    }

    static Node bucketSort(Node head, int n) {
        Node minNode = head, maxNode = head;
        int min = head.data, max = head.data;
        for (Node cur = head.next; cur != null; cur = cur.next) {
            if (cur.data < min) { min = cur.data; minNode = cur; }
            if (cur.data > max) { max = cur.data; maxNode = cur; }
        }

        if (min == max) return head;

        int range = max - min + 1;
        int bucketCount = Math.max(1, (int) Math.sqrt(n));
        @SuppressWarnings("unchecked")
        Node[] buckets = new Node[bucketCount];
        Node[] bucketTails = new Node[bucketCount];

        for (Node cur = head; cur != null; ) {
            Node nxt = cur.next;
            cur.next = null;
            int bucketIdx = bucketCount == 1 ? 0 : (int) ((long)(cur.data - min) * bucketCount / range);
            bucketIdx = Math.max(0, Math.min(bucketIdx, bucketCount - 1));
            if (buckets[bucketIdx] == null) buckets[bucketIdx] = cur;
            else bucketTails[bucketIdx].next = cur;
            bucketTails[bucketIdx] = cur;
            cur = nxt;
        }

        Node newHead = null, newTail = null;
        for (int i = 0; i < bucketCount; i++) {
            if (buckets[i] == null) continue;
            Node sorted = insertionSort(buckets[i]);
            if (newHead == null) newHead = sorted;
            else newTail.next = sorted;
            Node end = sorted;
            while (end.next != null) end = end.next;
            newTail = end;
        }
        return newHead;
    }

    static Node insertionSort(Node head) {
        Node sorted = null;
        for (Node cur = head; cur != null; ) {
            Node nxt = cur.next;
            if (sorted == null || cur.data <= sorted.data) {
                cur.next = sorted;
                sorted = cur;
            } else {
                Node prev = sorted, temp = sorted.next;
                while (temp != null && temp.data < cur.data) {
                    prev = temp;
                    temp = temp.next;
                }
                cur.next = temp;
                prev.next = cur;
            }
            cur = nxt;
        }
        return sorted;
    }
}
