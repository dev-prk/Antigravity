class AgeNotEligibleException(Exception):
    pass

def check_voting_eligibility(age):
    if age < 18:
        raise AgeNotEligibleException()
    else:
        print("Eligible for Voting")

try:
    age = int(input().strip())
    check_voting_eligibility(age)
except AgeNotEligibleException:
    print("Not Eligible for Voting")
except ValueError:
    print("Not Eligible for Voting")
