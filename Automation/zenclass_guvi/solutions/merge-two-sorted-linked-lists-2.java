import java.io.*;
import java.util.*;

public class Main {
    static class ListNode {
        int val;
        ListNode next;
        ListNode(int val) {
            this.val = val;
        }
    }

    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st;
        
        int n = Integer.parseInt(br.readLine().trim());
        ListNode head1 = null, tail1 = null;
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < n; i++) {
            int val = Integer.parseInt(st.nextToken());
            if (head1 == null) {
                head1 = new ListNode(val);
                tail1 = head1;
            } else {
                tail1.next = new ListNode(val);
                tail1 = tail1.next;
            }
        }
        
        int m = Integer.parseInt(br.readLine().trim());
        ListNode head2 = null, tail2 = null;
        st = new StringTokenizer(br.readLine());
        for (int i = 0; i < m; i++) {
            int val = Integer.parseInt(st.nextToken());
            if (head2 == null) {
                head2 = new ListNode(val);
                tail2 = head2;
            } else {
                tail2.next = new ListNode(val);
                tail2 = tail2.next;
            }
        }
        
        ListNode merged = mergeTwoLists(head1, head2);
        
        StringBuilder sb = new StringBuilder();
        ListNode curr = merged;
        while (curr != null) {
            sb.append(curr.val);
            if (curr.next != null) {
                sb.append(" ");
            }
            curr = curr.next;
        }
        sb.append(" ");
        System.out.println(sb.toString());
    }
    
    public static ListNode mergeTwoLists(ListNode l1, ListNode l2) {
        ListNode dummy = new ListNode(0);
        ListNode tail = dummy;
        
        while (l1 != null && l2 != null) {
            if (l1.val <= l2.val) {
                tail.next = l1;
                l1 = l1.next;
            } else {
                tail.next = l2;
                l2 = l2.next;
            }
            tail = tail.next;
        }
        
        if (l1 != null) {
            tail.next = l1;
        } else if (l2 != null) {
            tail.next = l2;
        }
        
        return dummy.next;
    }
}
