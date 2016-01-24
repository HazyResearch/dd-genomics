#! /usr/bin/env python

import sys

if len(sys.argv) != 4:
    print 'Wrong number of arguments'
    print 'USAGE: ./compute_stats_helper.py $label_tsvfile $prediction_tsvfile $confidence'
    exit(1)

label_filename = sys.argv[1]
pred_filename = sys.argv[2]
confidence = float(sys.argv[3])

# read label filename 
labels = {}
with open(label_filename) as f:
    for i, line in enumerate(f):
        line = line.split('\t')
        relationid = line[0].lower().strip()
        is_correct = line[1].lower().strip()
        if is_correct == 't':
            labels[mentionid] = True
        elif is_correct == 'f':
            labels[mentionid] = False

# read predictions 
predictions = {}
with open(pred_filename) as f:
    for i, line in enumerate(f):
        line = line.split('\t')
        relationid = line[0].lower().strip()
        expectation = line[1].strip()
        predictions[relationid] = (expectation >= 0.5)

# Evaluate number of true positives

true_positives = 0
true_negatives = 0
false_positives = 0
false_negatives = 0

for label_id in labels:
    # if the labeled mention is in the prediction set
    if label_id in predictions:
        if labels[label_id] and predictions[label_id]:
            true_positives += 1
        elif (not labels[label_id]) and predictions[label_id]:
            false_positives += 1
        elif labels[label_id] and not predictions[label_id]:
            false_negatives += 1
        else:
            true_negatives += 1
    # if the labeled mention is not in the prediction set (was ruled out)
    else:
        if labels[label_id]:
            # was true but rejected
            false_negative += 1
        else:
            true_negatives += 1 

# Print these
print 'True positives:\t'+str(true_positives)
print 'True negatives:\t'+str(true_negatives)
print 'False positives:\t'+str(false_positives)
print 'False negatives:\t'+str(false_negatives)
print '\n\n\n'

# compute precision, recall and F1
precision = float(true_positives)/float(true_positives+false_positives)
recall = float(true_positives)/float(true_positives+false_negatives)
F1_score = 2*float(true_positives) / (2*float(true_positives + false_positives + false_negatives))

print 'Precision:\t'+str(precision)
print 'Recall:\t'+str(recall)
print 'F1 score:\t'+str(F1_score)




