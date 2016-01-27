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
id2labeler = {}
labelers = set()
with open(label_filename) as f:
    for i, line in enumerate(f):
        line = line.split('\t')
        relationid = line[0].lower().strip()
        is_correct = line[1].lower().strip()
        labeler = line[2].strip()
	id2labeler[relationid] = labeler
	if labeler not in labelers:
	    labelers.add(labeler)
	if is_correct == 't':
            labels[relationid] = True
        elif is_correct == 'f':
            labels[relationid] = False

# read predictions 
predictions = {}
with open(pred_filename) as f:
    for i, line in enumerate(f):
        line = line.split('\t')
        relationid = line[0].lower().strip()
        expectation = float(line[1].strip())
        predictions[relationid] = expectation

# Evaluate number of true/false positives/negative

true_positives_total = 0
true_negatives_total = 0
false_positives_total = 0
false_negatives_total = 0

# evaluate number of true/false positives/negatives per labeler
labeler2FP = {}
labeler2TP = {}
labeler2FN = {}
labeler2TN = {}
for labeler in labelers:
    labeler2FP[labeler] = 0
    labeler2TP[labeler] = 0
    labeler2FN[labeler] = 0
    labeler2TN[labeler] = 0

# Count
for label_id in labels:
    # if the labeled mention is in the prediction set
    if label_id in predictions:
        if labels[label_id] and predictions[label_id] >= confidence:
            true_positives_total += 1
            labeler2TP[id2labeler[label_id]] += 1
        elif (not labels[label_id]) and predictions[label_id] >= confidence:
            false_positives_total += 1
            labeler2FP[id2labeler[label_id]] += 1
        elif labels[label_id] and not predictions[label_id] >= confidence:
            false_negatives_total += 1
            labeler2FN[id2labeler[label_id]] += 1
        else:
            true_negatives_total += 1
            labeler2TN[id2labeler[label_id]] += 1
    # if the labeled mention is not in the prediction set (was ruled out)
    else:
        if labels[label_id]:
            # was true but rejected
            false_negatives_total += 1
            labeler2FN[id2labeler[label_id]] += 1
        else:
            true_negatives_total += 1 
            labeler2TN[id2labeler[label_id]] += 1

# Print the total ones
print '##### SUMMARY #####'
print 'True positives:\t'+str(true_positives_total)
print 'True negatives:\t'+str(true_negatives_total)
print 'False positives:\t'+str(false_positives_total)
print 'False negatives:\t'+str(false_negatives_total)
print '\n'

# compute precision, recall and F1
precision = float(true_positives_total)/float(true_positives_total+false_positives_total)
recall = float(true_positives_total)/float(true_positives_total+false_negatives_total)
F1_score = 2*precision*recall / (precision+recall)

print 'Precision:\t'+str(precision)
print 'Recall:\t'+str(recall)
print 'F1 score:\t'+str(F1_score)
print '\n'
# Now do the same for every labeler

for labeler in labelers:
    print '##### '+labeler+' #####'
    print 'True positives:\t'+str(labeler2TP[labeler])
    print 'True negatives:\t'+str(labeler2TN[labeler])
    print 'False positives:\t'+str(labeler2FP[labeler])
    print 'False negatives:\t'+str(labeler2FN[labeler])
    print '\n'

    # test for precision for robustness
    if labeler2TP[labeler] + labeler2FP[labeler] > 0:
        precision = float(labeler2TP[labeler])/float(labeler2TP[labeler]+labeler2FP[labeler])
    else:
        precision = 'N/A (not enough examples)'
    # test for recall for robustness
    if labeler2TP[labeler] + labeler2FN[labeler] > 0:
        recall = float(labeler2TP[labeler])/float(labeler2TP[labeler]+labeler2FN[labeler])
    else:
        recall = 'N/A (not enough examples)'
    # test for F1 for robustness
    if (labeler2TP[labeler] + labeler2FP[labeler] > 0) and (labeler2TP[labeler] + labeler2FN[labeler] > 0) :
        F1_score = 2*precision*recall / (precision+recall)
    else:
        F1_score = 'N/A (not enough examples)'

    print 'Precision:\t'+str(precision)
    print 'Recall:\t'+str(recall)
    print 'F1 score:\t'+str(F1_score)
    print '\n'







































