-- Q3: Question 3  List all vendors that provide 'Catering' services.
SELECT id, vendor_name, service_type FROM vendors WHERE service_type = 'Catering';
