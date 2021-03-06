import json
import data_util
import generate_data
from plot_confusion_matrix import cm_analysis
import natural_logic_model as nlm

def example_overlap(premise, hypothesis):
    count = 0
    if premise.subject_adjective != hypothesis.subject_adjective and premise.subject_adjective != "" and  hypothesis.subject_adjective!= "":
        count = 1
    if premise.subject_noun != hypothesis.subject_noun:
        count = 2
    if premise.adverb != hypothesis.adverb and premise.adverb != "" and hypothesis.adverb != "":
        count = 3
    if premise.verb != hypothesis.verb:
        count = 4
    if premise.object_adjective != hypothesis.object_adjective and premise.object_adjective != "" and  hypothesis.object_adjective!= "":
        count = 5
    if premise.object_noun != hypothesis.object_noun:
        count = 6
    return count

def example_overlap2(premise, hypothesis):
    count = 0
    if premise.subject_noun == hypothesis.subject_noun:
        count += 1
    if premise.object_noun == hypothesis.object_noun:
        count += 1
    if premise.verb == hypothesis.verb:
        count += 1
    if premise.subject_adjective== hypothesis.subject_adjective or hypothesis.subject_adjective =="" or premise.subject_adjective=="":
        count += 1
    if premise.object_adjective== hypothesis.object_adjective or hypothesis.object_adjective =="" or premise.object_adjective=="":
        count += 1
    if premise.adverb== hypothesis.adverb or hypothesis.adverb == "" or premise.adverb == "":
        count += 1
    return count

data, _, _ = generate_data.process_data(1.0)
labels = ["entails", "contradicts", "permits"]
experiment = "experiment1_level2attention"
with open("meme", "r") as f:
    training_data, predictions = json.loads(f.read())
examples = []
true_labels = []
with open( experiment + ".val", "r") as f:
    for line in f:
        examples.append(json.loads(line))
        true_labels.append(json.loads(line)["gold_label"])
label_predictions = []
for p in predictions:
    label_predictions.append(labels[p])
#cm_analysis(true_labels, label_predictions, "simple_confuse.png", labels)
mistakes = [0] * 7
successes = [0] * 7
totals = [0] * 7
x = dict()
y = dict()
for label in labels:
    x[label] = dict()
for label in labels:
    y[label] = dict()
cont = set()
for i in range(len(examples)):
    premise = data_util.parse_sentence(data, examples[i]["sentence1"])[0]
    hypothesis = data_util.parse_sentence(data,examples[i]["sentence2"])[0]
    tup = (hypothesis.subject_adjective == "",hypothesis.object_adjective == "", hypothesis.adverb == "",premise.subject_adjective == "",premise.object_adjective == "", premise.adverb == "", premise.subject_determiner, premise.negation, premise.object_determiner, hypothesis.subject_determiner, hypothesis.negation, hypothesis.object_determiner)
    if examples[i]["gold_label"] == "contradicts" or examples[i]["gold_label"] == "entails":
        cont.add(tup)
for i in range(len(examples)):
    premise = data_util.parse_sentence(data, examples[i]["sentence1"])[0]
    hypothesis = data_util.parse_sentence(data,examples[i]["sentence2"])[0]
    tup = (hypothesis.subject_adjective == "",hypothesis.object_adjective == "", hypothesis.adverb == "",premise.subject_adjective == "",premise.object_adjective == "", premise.adverb == "", premise.subject_determiner, premise.negation, premise.object_determiner, hypothesis.subject_determiner, hypothesis.negation, hypothesis.object_determiner)
    if tup in cont and examples[i]["gold_label"] == "permits" and label_predictions[i] == "permits":
        meme2 = 0
        #print(premise.string)
        #print(hypothesis.string)

for i in range(len(examples)):
    premise = data_util.parse_sentence(data, examples[i]["sentence1"])[0]
    hypothesis = data_util.parse_sentence(data,examples[i]["sentence2"])[0]
    if examples[i]["gold_label"] == "permits" and label_predictions[i] != examples[i]["gold_label"] and example_overlap(premise,hypothesis) == 6 and False:
        print(premise.string)
        print(label_predictions[i])
        print(hypothesis.string)
    tup = (hypothesis.subject_adjective == "",hypothesis.object_adjective == "", hypothesis.adverb == "",premise.subject_adjective == "",premise.object_adjective == "", premise.adverb == "", premise.subject_determiner, premise.negation, premise.object_determiner, hypothesis.subject_determiner, hypothesis.negation, hypothesis.object_determiner)
    #tup = (hypothesis.subject_adjective == "",hypothesis.object_adjective == "", hypothesis.adverb == "",premise.subject_adjective == "",premise.object_adjective == "", premise.adverb == "")
    #tup = (premise.subject_determiner, premise.negation, premise.object_determiner, hypothesis.subject_determiner, hypothesis.negation, hypothesis.object_determiner)
    if tup == (True, True, False, False, False, False, 'some', 'does not', 'every', 'not every', 'does not', 'not every') and False:
        print(premise.string)
        print(label_predictions[i], examples[i]["gold_label"])
        print(hypothesis.string)
    for l in labels:
        if tup not in x[l]:
            x[l][tup] = 0
            y[l][tup] = 0
    if examples[i]["gold_label"] == label_predictions[i] and examples[i]["gold_label"]!="permits" and False:
        print(premise.string)
        print(label_predictions[i], examples[i]["gold_label"])
        print(hypothesis.string)
    if examples[i]["gold_label"] == label_predictions[i] or examples[i]["gold_label"]=="permits" or True:
        x[labels[predictions[i]]][tup] += 1
    if examples[i]["gold_label"] != labels[predictions[i]]:
        y[labels[predictions[i]]][tup] += 1
    if examples[i]["gold_label"] == "permits" and tup in cont:
        premise = data_util.parse_sentence(data, examples[i]["sentence1"])[0]
        hypothesis = data_util.parse_sentence(data,examples[i]["sentence2"])[0]
        totals[example_overlap(premise, hypothesis)] +=1
        if labels[predictions[i]] != examples[i]["gold_label"]:
            mistakes[example_overlap(premise, hypothesis)] +=1
        else:
            successes[example_overlap(premise, hypothesis)] +=1
for i in range(7):
    print(i, totals[i])
    if totals[i] != 0:
        print(mistakes[i]/totals[i], successes[i]/totals[i])
print(sum(mistakes)/sum(totals))
print(meme)
num = 0
total = 0
for k in y["entails"]:
    x2 = (x["entails"][k], x["contradicts"][k], x["permits"][k])
    if sum([y[l][k] for l in labels]) != 0:
        print(sum([y[l][k] for l in labels])/sum(x2),sum(x2),k )
for k in x["entails"]:
    x2 = (x["entails"][k], x["contradicts"][k], x["permits"][k])
    total += sum(x2)
    if x2[0] != 0 and (x2[1] != 0 or x2[2] != 0):
        print(x2)
        print(k)
        num+= sum(x2)
    elif x2[1] != 0 and (x2[0] != 0 or x2[2] != 0):
        print(x2)
        print(k)
        num+= sum(x2)
    elif x2[2] != 0 and (x2[1] != 0 or x2[0] != 0):
        print(x2)
        print(k)
        num+= sum(x2)
print(total, num, "meme")

for k in x["entails"]:
    print("\n")
    print(k)
    print(x["entails"][k], x["contradicts"][k], x["permits"][k])
    print("\n")
    _ = input("hi")
conjs = dict()
totals = dict()
es = dict()
badbools = [('or', 'or', 'equivalence', 'independence'), ('then', 'then', 'equivalence', 'independence'), ('then', 'and', 'equivalence', 'independence'), ('and', 'then', 'equivalence', 'independence'), ('and', 'and', 'equivalence', 'independence'), ('or', 'or', 'entails', 'independence'), ('and', 'then', 'entails', 'independence'), ('and', 'and', 'entails', 'independence'), ('then', 'then', 'reverse entails', 'independence'), ('then', 'and', 'reverse entails', 'independence'), ('and', 'or', 'reverse entails', 'independence'), ('and', 'then', 'reverse entails', 'independence'), ('and', 'and', 'reverse entails', 'independence'), ('or', 'then', 'contradiction', 'independence'), ('or', 'and', 'contradiction', 'independence'), ('then', 'or', 'contradiction', 'independence'), ('and', 'or', 'contradiction', 'independence'), ('then', 'or', 'cover', 'independence'), ('and', 'or', 'cover', 'independence'), ('and', 'then', 'cover', 'independence'), ('and', 'and', 'cover', 'independence'), ('or', 'then', 'alternation', 'independence'), ('or', 'and', 'alternation', 'independence'), ('and', 'or', 'alternation', 'independence'), ('or', 'or', 'independence', 'equivalence'), ('or', 'then', 'independence', 'equivalence'), ('then', 'then', 'independence', 'equivalence'), ('and', 'and', 'independence', 'equivalence'), ('or', 'or', 'independence', 'entails'), ('or', 'then', 'independence', 'entails'), ('then', 'then', 'independence', 'entails'), ('and', 'and', 'independence', 'entails'), ('and', 'or', 'independence', 'reverse entails'), ('and', 'then', 'independence', 'reverse entails'), ('and', 'and', 'independence', 'reverse entails'), ('or', 'and', 'independence', 'contradiction'), ('then', 'and', 'independence', 'contradiction'), ('and', 'or', 'independence', 'contradiction'), ('and', 'then', 'independence', 'contradiction'), ('and', 'or', 'independence', 'cover'), ('and', 'then', 'independence', 'cover'), ('and', 'and', 'independence', 'cover'), ('or', 'and', 'independence', 'alternation'), ('then', 'and', 'independence', 'alternation'), ('and', 'or', 'independence', 'alternation'), ('and', 'then', 'independence', 'alternation'), ('and', 'or', 'independence', 'independence'), ('and', 'or', 'independence', 'independence'), ('and', 'then', 'independence', 'independence'), ('and', 'then', 'independence', 'independence'), ('and', 'and', 'independence', 'independence'), ('and', 'and', 'independence', 'independence')]
badbools = set(badbools)
relations = ["equivalence", "entails", "reverse entails", "alternation","contradiction", "cover",  "independence"]
relations2 = ["equivalence", "entails", "reverse entails", "alternation","contradiction", "cover", "independence"]
for c1 in ["and", "or", "then"]:
    for c2 in ["and", "or", "then"]:
        for r1 in relations:
            for r2 in relations2:
                conjs[(c1,c2,r1,r2)] = [0,set()]
                totals[(c1,c2,r1,r2)] = 0
                es[(c1,c2,r1,r2)] = 0
for i in range(len(true_labels)):
    premise_parse = data_util.parse_sentence(data,examples[i]["sentence1"])
    hypothesis_parse = data_util.parse_sentence(data,examples[i]["sentence2"])
    if true_labels[i] != label_predictions[i] and true_labels[i] != "permits":
        conjs[(data_util.parse_sentence(data,examples[i]["sentence1"])[1],data_util.parse_sentence(data,examples[i]["sentence2"])[1], nlm.compute_simple_relation(premise_parse[0], hypothesis_parse[0]),nlm.compute_simple_relation(premise_parse[2], hypothesis_parse[2]))][0] += 1
        conjs[(data_util.parse_sentence(data,examples[i]["sentence1"])[1],data_util.parse_sentence(data,examples[i]["sentence2"])[1], nlm.compute_simple_relation(premise_parse[0], hypothesis_parse[0]),nlm.compute_simple_relation(premise_parse[2], hypothesis_parse[2]))][1].add((true_labels[i],label_predictions[i]))
    totals[(data_util.parse_sentence(data,examples[i]["sentence1"])[1],data_util.parse_sentence(data,examples[i]["sentence2"])[1], nlm.compute_simple_relation(premise_parse[0], hypothesis_parse[0]),nlm.compute_simple_relation(premise_parse[2], hypothesis_parse[2]))] += 1

meme = 0
for k in badbools:
    meme +=totals[k]
print("meme", meme)

print("fuck", len(badbools))
a = 0
b = 0
count = 0
for k in badbools:
    if k not in conjs:
        print(k, "fuck")

for k in conjs:
    if k in badbools:
        count +=conjs[k][0]
    if conjs[k][0] != 0 :
        print(k,conjs[k], conjs[k][0]/totals[k])
        a +=1
    else:
        b+=1
print(a,b,a/(a+b), b/(a+b))
print(count/(a+b))
print(hey)
