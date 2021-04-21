'''
Finding Similar Items: Textually Similar Documents
Author: Bazil Muzaffar Kotriwala
Timestamp: 27 Oct 2020 - 9 Nov 2020
All data used  has been retrieved from https://www.gutenberg.org/
'''

# Importing libraries
import os
import string
import re
import random
import binascii
import numpy as np
from itertools import combinations
from timeit import default_timer as timer


def read_preprocess_documents(n, data_dir, books_list):
    '''
    This function parses the number of books specified by the user line by line and cleans the it as required. It
    removes the punctuations, blank lines, converts all text to lowercase and then stores the cleaned book in a
    dictionary as key, value pairs, where key = book_name and value = cleaned_book (as a string).
    :param n: number of books to compare selected by the user
    :param data_dir: the directory where the books are located
    :param books_list: contains the name of the book files (all books are in .txt format)
    :return: a dictionary containing the ({book name: cleaned book string}) as key, value pairs ready to be used
    to create shingles as a next step.
    '''

    parsed_books = {}
    for i in range(n):
        clean_doc = []
        with open(os.path.join(data_dir, books_list[i]), "r", encoding='utf-8') as f:
            doc_text = f.readlines()
            for j in range(1, len(doc_text)):
                curr_str = doc_text[j].translate(str.maketrans('', '', string.punctuation)).replace("’", '') \
                    .strip('\n').lstrip(' ').lower()
                curr_str = re.sub(' +', ' ', curr_str)
                if curr_str != '':
                    clean_doc.append(curr_str)
            parsed_books[books_list[i].replace('.txt', '')] = ' '.join(clean_doc).replace(' ', '_')
    return parsed_books


def shingling(s, k):
    '''
    Constructs k-shinglings at character level and all spaces are replaced by '_' as shown in the lecture. The shingles
    are created of length k which is inputted by the user. The hash value is calculated for each shingle and stored in
    a set.
    :param s: the book retrieved as a string
    :param k: the length k for the shingles inputted by the user
    :return: A set of hashed k-shingles for the specific book 's'
    '''

    h_shingles_set = set()
    for i in range(len(s) - k + 1):
        hashed_shingle = binascii.crc32((s[i:i+k]).encode()) & 0xffffffff
        if hashed_shingle not in h_shingles_set:
            h_shingles_set.add(hashed_shingle)
    return h_shingles_set


def compare_sets(set1, set2):
    '''
    Computes the Jaccard similarity of two sets of integers – two sets of hashed shingles.
    :param set1: Set of hashed shingles for book 1
    :param set2: Set of hashed shingles for book 2
    :return: Jaccard similarity
    '''

    jaccard_similarity = len(set1.intersection(set2)) / len(set1.union(set2))
    return jaccard_similarity


def generate_random_coefficient(max_hash_value, no_of_hash_functions):
    '''
    This function generates the coefficient's 'a' or 'b' which are to be used in the hash function h(x) = (ax + b) % c
    in min-hashing. It generates the number of values equal to the number of hash functions (default is 100).
    :param max_hash_value: Max hash bucket number derived from the range (0 - 2**32 - 1)
    :param no_of_hash_functions: The number of independent hash functions to be used (100 as default)
    :return: A list of randomly generated numbers between 0 - (2**32 - 1), where len of list equals to no_of_hash_functions
    '''

    tmp = set()
    random_numbers_list = []

    for i in range(no_of_hash_functions):
        random_num = random.randint(0, max_hash_value)
        if random_num not in tmp:
            tmp.add(random_num)
            random_numbers_list.append(random_num)
        else:
            # Re-generate random num
            while random_num in tmp:
                random_num = random.randint(0, max_hash_value)
            random_numbers_list.append(random_num)
    return random_numbers_list


def min_hashing(hashed_shingle_set, no_of_hash_functions, max_hash_value):
    '''
    This function builds a minHash signature in the form of a vector from a set of hashed shingles. It applies a total
    of 100 independent hash functions h(x) = (ax + b) % c on every shingle and stores the minimum hash value
    for every shingle in the signature vector. The signature vector is built using numpy.
    :param hashed_shingle_set: A book whose shingles have been hashed and stored in a set
    :param no_of_hash_functions: The number of independent hash functions to be used (100 as default)
    :param max_hash_value: Max hash bucket number derived from the range (0 - 2**32 - 1)
    :return: The signature vector containing the minimum hash value for each shingle.
    '''

    signatures_list = []
    for i in range(no_of_hash_functions):
        min_hash_value = None
        for hash_shingle in hashed_shingle_set:
            hash_value = ((random_coefficients_a[i] * hash_shingle) + random_coefficients_b[i]) % max_hash_value
            if min_hash_value is None:
                min_hash_value = hash_value
            elif hash_value < min_hash_value:
                min_hash_value = hash_value
        signatures_list.append(min_hash_value)
    return np.array(signatures_list)


def compare_signatures(minhash_signatures1, minhash_signatures2):
    '''
    This function estimates the similarity of two integer vectors – minhash signatures – as a fraction of components,
    in which they agree.
    :param minhash_signatures1: Set of minhashed signatures for book 1
    :param minhash_signatures2: Set of minhashed signatures for book 2
    :return: The similarity score estimate which is calculated by retrieving the minhash values which are the same in
    both minhash_signatures1 and minhash_signatures2 and dividing them by the total number of signatures.
    '''

    # Compare only if the minhash signatures agree
    assert len(minhash_signatures1) == len(minhash_signatures2), "The vector sizes are not the same"
    return len(np.intersect1d(minhash_signatures1, minhash_signatures2)) / len(minhash_signatures1)


if __name__ == '__main__':

    # Ask user for input for number of books, k-shingles length, and similarity threshold 's'
    print("Let's find similar books!\n")
    nums = {2, 3, 4, 5, 6, 7, 8, 9, 10}
    while True:
        num_of_books = int(input("\nEnter the number of books you want to compare (2 - 10), press 0 to quit: "))
        if num_of_books == 0:
            print('\n The Program has been terminated')
            break

        k = int(input("\nEnter the value for k-shingles of a given length (2 - 10), press 0 to quit: "))
        if k == 0:
            print('\n The Program has been terminated')
            break

        s = float(input("\nEnter the similarity threshold value (0.1 - 0.99), press 0 to quit: "))
        print('\n')
        if s == 0:
            print('\n The Program has been terminated')
            break

        if num_of_books in nums and k in nums:

            # Initialize directories
            data_dir = os.path.join(os.getcwd(), 'data')
            books_list = os.listdir(data_dir)

            start_time = timer()

            # Read and preprocess the documents and insert them into a dictionary
            parsed_docs_map = read_preprocess_documents(num_of_books, data_dir, books_list)
            print('Books Selected:')
            for i, book in enumerate(list(parsed_docs_map.keys())):
                print(str(i+1) + '.', book)
            print('\n')

            # Clean book names for output
            user_books_list = []
            for book in books_list[:num_of_books]:
                user_books_list.append(book.replace('.txt', ''))

            # Initialize values
            shingles_docs = {}
            hashed_shingles_docs = {}
            no_of_hash_functions = 100
            max_hash_value = (2 ** 32) - 1

            # Compute the shingles for the number of books selected by the user and store them in a dictionary
            # Makes use of the shingling function defined above
            for book in user_books_list:
                hashed_shingles_docs[book] = shingling(parsed_docs_map[book], k)

            # For the hash function to be used in min-hashing, we generate the coefficients a and b (100 co-effs each)
            random_coefficients_a = generate_random_coefficient(max_hash_value, no_of_hash_functions)
            random_coefficients_b = generate_random_coefficient(max_hash_value, no_of_hash_functions)

            # Compute the min hash values for each book and storing them as key, value in dictionary
            # where key = book name and value = min_hashed_signatures_vector for that book
            print('Performing min hashing...')
            min_hashed_shingles_docs = {}
            for book in user_books_list:
                min_hashed_shingles_docs[book] = min_hashing(hashed_shingles_docs[book], no_of_hash_functions, max_hash_value)
            print('Done\n')

            # Create the unique combinations of books which can be compared with each other
            # e.g. [(book1, book2), (book1, book3), (book2, book3) ...] etc depending on input parameters by user
            unique_doc_combinations = list(combinations([x for x in list(parsed_docs_map.keys())], 2))

            # Compute scores and categorize them between similar and non-similar books based on threshold input by the user
            print('Comparing book similarity scores...')
            sim_books = []
            not_sim_books = []
            for combination in unique_doc_combinations:
                sim_score = compare_signatures(min_hashed_shingles_docs[combination[0]], min_hashed_shingles_docs[combination[1]])
                if sim_score >= s:
                    sim_books.append((combination[0], combination[1], sim_score))
                else:
                    not_sim_books.append((combination[0], combination[1], sim_score))
            print('Done\n')

            # Code to print output clearly
            print('----------- Similar Books (s threshold >=', s, ') ----------------')
            if sim_books == []:
                print('No similar books found! Try again with different value for no of books and k')
            else:
                for book_tuple in sim_books:
                    print('The similarity score between', book_tuple[0], 'and', book_tuple[1], '=', book_tuple[2])

            print('\n----------- Not Similar Books (s threshold <', s, '----------------')
            if not_sim_books == []:
                print('No dis-similar books found! Try again with different value for no of books and k')
            else:
                for book_tuple in not_sim_books:
                    print('The similarity score between', book_tuple[0], 'and', book_tuple[1], '=', book_tuple[2])
            print("\nTotal Running Time: ", round(timer() - start_time, 2), 'seconds')
        else:
            print('\n Option does not exist. Please try again with an option from 2-10. \n')