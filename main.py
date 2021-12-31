import csv
from itertools import combinations
import sys

min_support = 0.0
min_confidence = 0.0
dataset = ''


def get_candidates(prev_L):
    # Receives a list of items and returns a set of combinations of those items.

    ck = set()
    for a in prev_L:
        for b in prev_L:
            good_set = set(set().union(a, b))
            if len(good_set) == (len(prev_L[0]) + 1):
                tup = tuple(sorted(list(good_set)))
                ck.add(tup)
    return ck


def calculate_next_L(L, L_with_frequency, transactions):
    # Calculates the next L which is a list of combinations of items with their supports and returns it.

    prev_L = L
    L = L
    while len(prev_L) > 0:
        ck = get_candidates(prev_L)
        frequency = {}
        for transaction in transactions:
            for good_set in ck:
                if set(list(good_set)) <= set(transaction):
                    frequency[good_set] = frequency.get(good_set, 0) + 1

        cur_L = []
        for key, value in frequency.items():
            if value >= min_support * len(transactions):
                cur_L.append(key)
                L_with_frequency[tuple(key)] = value

        prev_L = cur_L
        L += cur_L
    return L_with_frequency


def get_rules(frequency):
    # Generates and returns the association rules having confidence greater than or equal to the minimum confidence.

    final_rules = {}
    for key, value in frequency.items():
        if len(key) > 1:
            for combo in combinations(key, len(key) - 1):
                confidence = value / float(frequency[combo])
                if confidence >= min_confidence:
                    final_rules[(combo, tuple(set(combo) ^ set(key)))] = confidence
    return final_rules


def apriori_algo(transactions):
    # Performs the A-priori algorithm described in Section 2.1 of the Agrawal and Srikant paper in VLDB 1994 to compute the frequent itemsets.

    L, L_with_frequency = get_first_L(transactions)
    L_with_frequency = calculate_next_L(L, L_with_frequency, transactions)
    final_rules = get_rules(L_with_frequency)
    return L_with_frequency, final_rules


def get_first_L(transactions):
    # Calculates frequent 1-itemsets.

    count = {}
    word_with_freq = {}
    for transaction in transactions:
        for word in transaction:
            count[word] = count.get(word, 0) + 1

    L = []
    for key, value in count.items():
        if value >= min_support * len(transactions):
            L.append([key])
            word_with_freq[(key + "",)] = value
    return L, word_with_freq


def get_all_transactions():
    # Gets all the rows in the dataset.

    transactions = []

    with open(dataset, 'r') as csvfile:
        csv_object = csv.reader(csvfile)
        i = 0
        for row in csv_object:
            temp_set = set()
            if i == 0:
                i = 1
            for r in row:
                temp_set.add(r)
            transactions.append(temp_set)
    return transactions


def main():
    global min_support, min_confidence, dataset
    dataset = sys.argv[1]
    min_support = float(sys.argv[2])
    min_confidence = float(sys.argv[3])

    print("min_sup: " + str(round(min_support,4)))
    print("min_conf: " + str(round(min_confidence,4)))

    transactions = get_all_transactions()
    frequent_itemsets, rules = apriori_algo(transactions)

    n = len(transactions)
    with open('output.txt', 'w') as file:
        file.write("\n==Frequent itemsets (min_sup=" + str(round(min_support * 100,4)) + "%)" + "\n\n")
        frequent_itemsets_sorted = dict(sorted(frequent_itemsets.items(), key=lambda item: -item[1]))
        for k, v in frequent_itemsets_sorted.items():
            file.write(str(k) + " " + str(round(v * 100 / n, 4)) + "%" + "\n")

        file.write("\n==High-confidence association rules (min_conf=" + str(round(min_confidence * 100,4)) + "%)" + "\n\n")
        rules_sorted = dict(sorted(rules.items(), key=lambda item: -item[1]))
        for k, v in rules_sorted.items():
            file.write('['+str(k[0])[1:-1] + " => " + str(k[1])[1:-1] + "] (Conf: " + str(round((v * 100), 4)) + "%, Supp:" + str(
                round((frequent_itemsets[k[0]] * 100 / n), 4)) + "%)" + "\n")


if __name__ == '__main__':
    main()