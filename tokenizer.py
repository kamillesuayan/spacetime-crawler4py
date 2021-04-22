import sys
import re

def stop_word():
    file = open('stop.txt', 'r')
    words = []
    for line in file:
        words.append(line.strip('\n'))
    file.close()
    return words

# time complexity: O(N*M). The nested for-loops iterate through each line,
# and then through each word on the lines, resulting in O(N*M) runtime complexity
def tokenize(text_string):
    result = []
    stp = stop_word()
    for word in text_string.split():
        if len(result) >= 50001:
            return result
        # print(word.lower() not in stp)
        #if word.lower().strip() not in stp:
        c_word = re.sub("[^a-zA-Z0-9\s]", "",word).lower() 
        if c_word != "" and c_word not in stp: 
            result.append(c_word)
    return result

# time complexity: O(N). We are just going through N tokens
def computeWordFreq(tokenList, freqs):
    for token in tokenList:
        if token in freqs:
            freqs[token] += 1
        else:   
            freqs[token] = 1
    #return freqs

# time complexity: O(N log N). Sorting the items in the dictionary
# takes the longest for this function
def freqs(freqMap):
    # adapted from: https://www.geeksforgeeks.org/python-sort-python-dictionaries-by-key-or-value/
    wordRank = sorted(freqMap.items(), key = lambda kv:(kv[1], kv[0]), reverse = True)
    ans = []
    for key, value in wordRank: # CHANGE BACK LATERRRRRRR
        ans.append(key)
    return ans
    #for word in wordRank:
        #print(word[0],"->",word[1])

# def commonTokens(txt1, txt2):
#     tkList_1 = set(pa.tokenize(txt1))
#     tkList_2 = set(pa.tokenize(txt2))
    
#     freq_intersect = list([word for word in tkList_1 if word in tkList_2])
#     print(freq_intersect)
#     print(len(freq_intersect))