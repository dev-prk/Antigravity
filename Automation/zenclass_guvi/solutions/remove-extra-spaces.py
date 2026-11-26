# Problem: Remove Extra Spaces

# Input: A sentence with extra spaces
sentence = input()

# Split the sentence into a list of words with spaces
words = sentence.split()

# Initialize an empty list to store the words without extra spaces
no_extra_spaces = []

# Iterate over each word in the list
for word in words:
    # Remove extra spaces from the word
    no_extra_spaces.append(word.strip())

# Join the words without extra spaces into a sentence
result = ' '.join(no_extra_spaces)

# Output the result
print(result)
