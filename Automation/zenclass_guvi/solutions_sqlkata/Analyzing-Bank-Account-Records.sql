-- Q1: Question 1  Display the customer(s) having the highest account balance.
SELECT CustomerName, Balance FROM BankAccount WHERE Balance = (SELECT MAX(Balance) FROM BankAccount);
