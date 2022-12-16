import re
import entropy_calculator


PERCENT_THRESHOLD = 10
MAX_THRESHOLD     = 70

LOWERCASE_LETTERS     = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE_LETTERS     = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALLOWED_CHARACTERS    = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=-"
UNCOMMON_LETTERS      = "wkxjqz"
UNCOMMON_LETTERS_COUNT_MINIMUM = 2



def false_positive(string):
	false_positive_status = False

	#is default string
	if "abcdefg" in string.lower():
		false_positive_status = True

	if "12345" in string.lower():
		false_positive_status = True





	#see if entropy level is high enough
	if entropy_calculator.score(string.lower()) < 4:
		false_positive_status = True





	#count uncommon letters
	uncommon_letters_count = 0
	for character in string:
		if character.lower() in UNCOMMON_LETTERS:
			uncommon_letters_count += 1

	if uncommon_letters_count < UNCOMMON_LETTERS_COUNT_MINIMUM:
		false_positive_status = True





	#count amount of each character type
	lowercase_count = 0
	uppercase_count = 0
	all_character_count = 0


	#check if enough letters are uppercase
	for character in string:

		#if has weird character, who cares?
		if character not in ALLOWED_CHARACTERS:
			false_positive_status = True

		else:
			if character in LOWERCASE_LETTERS: lowercase_count += 1
			if character in UPPERCASE_LETTERS: uppercase_count += 1
		
		all_character_count += 1



	#add to list if meets percent threshold
	if all_character_count:
		string_uppercase_percent = (100 * uppercase_count) / all_character_count


		if string_uppercase_percent < PERCENT_THRESHOLD:
			false_positive_status = True

		if string_uppercase_percent > MAX_THRESHOLD:
			false_positive_status = True




	return false_positive_status




def string_analysis(block):
	tokens = []

	#split by specific special characters
	strings = re.split(r'[`\~!@#$%^&*()\[\]{};\'\\:"|<,<>?= ]', block)

	for string in strings:

		#skip if not long enough
		if len(string) <= 20:
			continue

		#skip if too long
		if len(string) > 64:
			continue

		#skip already found
		if string in tokens:
			continue

		#reduce false positives
		if not false_positive(string):
			tokens.append(string)


	return tokens
