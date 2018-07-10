import random
import json
import os
import copy
import pickle
from nltk.sem.logic import *
from nltk.inference import *
from nltk import Prover9
from nltk.corpus import wordnet
from joblib import Parallel, delayed

class sentence:
    #this class stores the logical representation of a sentence and the natural language representation of a sentence
    def __init__(self, subject_noun, verb, object_noun, negate, adverb, subject_adjective, object_adjective, subject_determiner, object_determiner):
        self.subject_noun = subject_noun
        self.verb = verb
        self.object_noun = object_noun
        self.negate = negate
        self.subject_determiner = subject_determiner
        self.object_determiner = object_determiner
        self.string_object_determiner = object_determiner
        if negate and object_determiner == "no":
            self.string_object_determiner = "any"
        self.negation = ""
        self.adverb = adverb
        self.subject_adjective = subject_adjective
        self.object_adjective = object_adjective
        self.verb_index = 0
        if negate:
            self.negation = "does not" #negation for active
            self.verb_index = 2#controls the verb form
        self.string = self.construct_string([self.subject_determiner,self.subject_adjective,self.subject_noun,self.negation,self.adverb,self.verb[self.verb_index],self.string_object_determiner,self.object_adjective,self.object_noun])
        self.construct_logical_form()

    def construct_string(self,lst):
        #turn a list of words into a single sentence string
        result = ""
        for word in lst:
            if word != "":
                result += word + " "
        return result[:-1]

    def construct_logical_form(self):
        #construct a first order logic representation
        logical_form = ""
        subject_noun_variable= "x"
        object_noun_variable= "y"
        verb_arg = "(" + subject_noun_variable + "," + object_noun_variable + ")"
        logical_form = self.verb[2] + verb_arg
        if self.adverb != "" :
            logical_form ="(" +logical_form +  "&" + self.adverb + verb_arg + ")"
        object_logical_form = self.object_noun + "(" + object_noun_variable + ")"
        if self.object_adjective != "":
            object_logical_form = "(" + object_logical_form + "&" + self.object_adjective + "(" + object_noun_variable + ")" + ")"
        logical_form = self.add_quantifier(self.object_determiner, object_logical_form, logical_form)
        if self.negate:
            logical_form = "-" + "(" + logical_form + ")"
        subject_logical_form = self.subject_noun + "(" + subject_noun_variable + ")"
        if self.subject_adjective != "":
            subject_logical_form ="(" + subject_logical_form +  "&" + self.subject_adjective + "(" + subject_noun_variable +  ")" + ")"
        self.logical_form = self.add_quantifier(self.subject_determiner, subject_logical_form, logical_form)

    def add_quantifier(self, determiner, first_relation, second_realtion):
        result = ""
        if determiner == "some" or determiner == "no":
            result = "exists y.(" + first_relation + "&" + second_realtion + ")"
            if determiner == "no":
                result = "-(" + result + ")"
        if determiner == "every" or determiner == "not every":
            result = "all y.(" + first_relation + "->" + second_realtion + ")"
            if determiner == "not every":
                result = "-(" + result + ")"
        return result


def process_data(train_ratio):
    #split the different parts of speech into train, validation, and test
    #determiners are not split
    train = dict()
    val = dict()
    test = dict()
    categories = ["agents", "transitive_verbs", "things", "determiners", "adverbs", "subject_adjectives","object_adjectives"]
    for c in categories:
        with open(os.path.join("data", c + ".txt"),"r") as f:
            stuff = f.readlines()
            if c != "transitive_verbs":
                stuff = [_.strip() for _ in stuff]
            else:
                stuff = [_.strip().split() for _ in stuff]
        random.shuffle(stuff)
        if c != "determiners":
            train[c] = stuff[:int(len(stuff)*train_ratio)]
            val[c] = stuff[int(len(stuff)*train_ratio):int(len(stuff)*(train_ratio+(1-train_ratio)*0.5))]
            test[c] = stuff[int(len(stuff)*(train_ratio+(1-train_ratio)*0.5)):]
        else:
            train[c] = stuff
            val[c] = stuff
            test[c] = stuff
    return train, val, test

def get_label(prover, premise, hypothesis):
    #returns a label that is determined from using Prover9 on the first order logic representations
    p = Expression.fromstring(premise.logical_form)
    h = Expression.fromstring(hypothesis.logical_form)
    noth = Expression.fromstring("-" + "(" + hypothesis.logical_form + ")")
    if prover.prove(h, [p]):
        return "entails"
    if prover.prove(noth, [p]):
        return "contradicts"
    return "permits"

def build_simple_file():
    subject_noun = "man"
    subject_adjective1 = "tall"
    subject_adjective2 = "happy"
    adverb1 = "happily"
    adverb2 = "crazily"
    verb = ["eats", "eaten", "eat"]
    object_noun = "rock"
    object_adjective1 = "big"
    object_adjective2 = "rough"
    dets = ["every", "not every", "some", "no"]
    sentences = []
    encodings = []
    for pd1_index in range(4):
        pd1 = dets[pd1_index]
        for pd2_index in range(4):
            pd2 = dets[pd2_index]
            for hd1_index in range(4):
                hd1 = dets[hd1_index]
                for hd2_index in range(4):
                    hd2 = dets[hd2_index]
                    for subject_adjective_index in range(4):
                        if subject_adjective_index == 0:
                            padj1_word = subject_adjective1
                            hadj1_word = padj1_word
                        elif subject_adjective_index == 1:
                            padj1_word = ""
                            hadj1_word = subject_adjective2
                        elif subject_adjective_index == 2:
                            padj1_word = subject_adjective1
                            hadj1_word = ""
                        else:
                            padj1_word = subject_adjective1
                            hadj1_word = subject_adjective2
                        for object_adjective_index in range(4):
                            if object_adjective_index == 0:
                                padj2_word = object_adjective1
                                hadj2_word = padj2_word
                            elif object_adjective_index == 1:
                                padj2_word = ""
                                hadj2_word = object_adjective2
                            elif object_adjective_index == 2:
                                padj2_word = object_adjective1
                                hadj2_word = ""
                            else:
                                padj1_word = object_adjective1
                                hadj1_word = object_adjective2
                            for adverb_index in range(4):
                                if adverb_index == 0:
                                    padv_word = adverb1
                                    hadv_word = padv_word
                                elif adverb_index == 1:
                                    padv_word = ""
                                    hadv_word = adverb2
                                elif adverb_index == 2:
                                    padv_word = adverb1
                                    hadv_word = ""
                                else:
                                    padv_word = adverb1
                                    hadv_word = adverb2
                                for pnegation_value in range(2):
                                    for hnegation_value in range(2):
                                        sentences.append(
                                        [sentence(subject_noun, verb, object_noun, pnegation_value, padv_word, padj1_word, padj2_word, pd1,pd2),
                                        sentence(subject_noun, verb, object_noun, hnegation_value, hadv_word, hadj1_word, hadj2_word, hd1,hd2 )])
                                        encodings.append([pnegation_value, pd1_index,pd2_index, hnegation_value, hd1_index, hd2_index, subject_adjective_index, object_adjective_index, adverb_index])
    labels = Parallel(n_jobs=-1,backend="multiprocessing")(map(delayed(parallel_labels), sentences))
    result = dict()
    for i in range(len(labels)):
        final_encoding = encodings[i] + [1,1,1]
        result[json.dumps(final_encoding)] = labels[i]
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    if i != 1 or j != 1 or k != 1:
                        result[json.dumps(final_encoding + [i,j,k])] = "permits"
    with open("simple_examples" , "w") as f:
        f.write(json.dumps(result))

global_prover = Prover9()
global_prover.config_prover9(r"C:\Program Files (x86)\Prover9-Mace4\bin-win32")

def parallel_labels(x):
    label = get_label(global_prover, x[0], x[1])
    print(x[0].string, x[0].logical_form, label, x[1].string, x[1].logical_form)
    return label

def build_boolean_file():
    logic_operators = ["|", "&", "->"]
    result = dict()
    for pindex in range(3):
        for hindex in range(3):
            for first_relation in range(3):
                for second_relation in range(3):
                    first_predicate = "A"
                    second_predicate = "B"
                    first_assumption = "(" + first_predicate+"(constant)"+logic_operators[pindex] + second_predicate+"(constant)" + ")"
                    first_predicate = "C"
                    second_predicate = "D"
                    conclusion = "(" + first_predicate+"(constant)"+logic_operators[hindex] + second_predicate+"(constant)" + ")"
                    assumptions = [Expression.fromstring(first_assumption)]
                    if first_relation == 0:
                        assumptions.append(Expression.fromstring("A(constant)->C(constant)"))
                    if first_relation == 1:
                        assumptions.append(Expression.fromstring("-A(constant)|-C(constant)"))
                    if second_relation == 0:
                        assumptions.append(Expression.fromstring("B(constant)->D(constant)"))
                    if second_relation == 1:
                        assumptions.append(Expression.fromstring("-B(constant)|-D(constant)"))
                    label = None
                    if global_prover.prove(Expression.fromstring(conclusion), assumptions):
                        label = "entails"
                    elif global_prover.prove(Expression.fromstring("-"+conclusion), assumptions):
                        label = "contradicts"
                    else:
                        label = "permits"
                    result[json.dumps((pindex, hindex, first_relation, second_relation))] = label
    with open("boolean_data", "w") as f:
        f.write(json.dumps(result))



def generate_compound(examples, first_predicate, second_predicate, sample, sample_index, conjunction, logic_operator):
    order = random.randint(0,1)
    if order:
        temp = first_predicate
        first_predicate = second_predicate
        second_predicate = temp
    sentence = sample[order][sample_index] + " " + conjunction + " " + sample[not order][sample_index]
    if conjunction == "then":
        sentence = "if " + sentence
    logic_form = "(" + first_predicate+"(constant)"+logic_operator + second_predicate+"(constant)" + ")"
    return sentence, logic_form, order

def generate_boolean_examples(examples, size):
    prover = Prover9()
    prover.config_prover9(r"C:\Program Files (x86)\Prover9-Mace4\bin-win32")
    bool_examples = []
    conjunctions = ["or", "and", "then"]
    logic_operators = ["|", "&", "->"]
    for i in range(size):
        sample = random.sample(examples, 2)
        index = random.randint(0,2)
        prem_conjunction = conjunctions[index]
        logic_operator = logic_operators[index]
        premise, first_assumption, prem_order  = generate_compound(examples, "A", "B", sample, 0, prem_conjunction, logic_operator)
        index = random.randint(0,2)
        hyp_conjunction = conjunctions[index]
        logic_operator = logic_operators[index]
        hypothesis, conclusion, hyp_order = generate_compound(examples, "C", "D", sample, 2, hyp_conjunction, logic_operator)
        assumptions = [Expression.fromstring(first_assumption)]
        if sample[0][1] == "entails":
            assumptions.append(Expression.fromstring("A(constant)->C(constant)"))
        if sample[0][1] == "contradicts":
            assumptions.append(Expression.fromstring("-A(constant)|-C(constant)"))
        if sample[1][1] == "entails":
            assumptions.append(Expression.fromstring("B(constant)->D(constant)"))
        if sample[1][1] == "contradicts":
            assumptions.append(Expression.fromstring("-B(constant)|-D(constant)"))
        label = None
        if prover.prove(Expression.fromstring(conclusion), assumptions):
            label = "entails"
        elif prover.prove(Expression.fromstring("-"+conclusion), assumptions):
            label = "contradicts"
        else:
            label = "permits"
        bool_examples.append((premise, label, hypothesis, {"premise":[sample[prem_order][3]["premise"][0],sample[not prem_order][3]["premise"][0]],"hypothesis":[sample[hyp_order][3]["hypothesis"][0],sample[not hyp_order][3]["hypothesis"][0]], "prem_conjunction":prem_conjunction, "hyp_conjunction":hyp_conjunction}))
    return bool_examples


def save_data(examples, name):
    data = []
    for example in examples:
        example_dict = dict()
        example_dict["sentence1"] = example[0]
        example_dict["sentence2"] = example[2]
        example_dict["gold_label"] = example[1]
        example_dict["example_data"] = example[3]
        data.append(json.dumps(example_dict))
    with open(name, 'wb') as f:
        f.writelines(data)

def restricted(restrictions, enc):
    for i in range(len(enc)):
        if restrictions[i] < enc[i]:
            return True
    return False

def split_dict(filename, restrictions):
    with open(filename, 'r') as f:
        solutions= json.loads(f.read())
    e = dict()
    c = dict()
    p = dict()
    for i in examples:
        if restricted(restrictions,json.loads(i)):
            continue
        if solutions[i] == "entails":
            e[i] = examples[i]
        if solutions[i] == "contradicts":
            c[i] = stuff[i]
        if solutions[i] == "permits":
            p[i] = stuff[i]
    return e, c, p

def compute_relation(lexicon, relation_index):
    if relation_index == 0:
        premise_word = random.choice(lexicon)
        hypothesis_word = premise_word
    if relation_index == 1:
        premise_word = ""
        hypothesis_word = random.choice(lexicon)
    if relation_index == 3:
        premise_word = random.choice(lexicon)
        hypothesis_word = ""
    if relation_index == 3:
        premise_word = random.choice(lexicon)
        index = lexicon.index(premise_word)
        lexicon.remove(premise_word)
        hypothesis_word = random.choice(lexicon)
        lexicon.insert(index, premise_word)
    return premise_word, hypothesis_word



def encoding_to_example(data, encoding):
    dets = ["every", "not every", "some", "no"]
    psubject_noun = random.choice(data["agents"])
    pverb = random.choice(data["transitive_verbs"])
    pobject_noun = random.choice(data["things"])
    hsubject_noun = psubject_noun
    hverb = pverb
    hsubject_noun = psubject_noun
    if encoding[-3] == 0:
        hsubject_noun = select_new(data["agents"], hsubject_noun)
    if encoding[-2] == 0:
        hverb = select_new(data["transitive_verbs"], hverb)
    if encoding[-1] == 0:
        hobject_noun = select_new(data["agents"], hobject_noun)
    padverb, hadverb  = compute_relation(data["adverbs"], encoding[-4])
    pobject_adjective, hobject_adjective = compute_relation(data["object_adjectives"], encoding[-5])
    psubject_adjective, hsubject_adjective = compute_relation(data["subject_adjectives"], encoding[-6])
    return sentence(psubject_noun, pverb, pobject_noun, encoding[0], padverb, psubject_adjective, pobject_adjective, dets[enc[1]],dets[enc[2]]), sentence(hsubject_noun, hverb, hobject_noun, encoding[3], hadverb, hsubject_adjective, hobject_adjective, dets[enc[4]],dets[enc[5]])

def generate_boolean_data(boolkeys, ekeys, ckeys, pkeys, size, data):
    result = []
    for i in range(size):
        encoding = random.choice(boolkeys)
        if encoding[3] == 0:
            simple1_encoding = json.loads(random.choice(ekeys))
            premise1, hypothesis1 = encoding_to_example(data, simple1_encoding)
        if encoding[3] == 1:
            simple1_encoding = json.loads(random.choice(ckeys))
            premise1, hypothesis1 = encoding_to_example(data, simple1_encoding)
        if encoding[3] == 2:
            simple1_encoding = json.loads(random.choice(pkeys))
            premise1, hypothesis1 = encoding_to_example(data,simple1_encoding)
        if encoding[4] == 0:
            simple2_encoding = json.loads(random.choice(ekeys))
            premise2, hypothesis2 = encoding_to_example(data, simple2_encoding)
        if encoding[4] == 1:
            simple2_encoding = json.loads(random.choice(ckeys))
            premise2, hypothesis2 = encoding_to_example(data, simple2_encoding)
        if encoding[4] == 2:
            simple2_encoding = json.loads(random.choice(pkeys))
            premise2, hypothesis2 = encoding_to_example(data, simple2_encoding)
        if encoding[2] == 1:
            temp = premise2
            premise2 = premise1
            premise1 = temp
        conjunctions = ["or", "and", "then"]
        premise_conjunction = conjunctions[encoding[0]]
        hypothesis_conjunction = conjunctions[encoding[1]]
        premise_compound = premise1.string + " " + premise_conjunction + " " + premise2.string
        hypothesis_compound = hypothesis1.string+ " " + hypothesis_conjunction+ " " + hypothesis2.string
        if premise_conjunction == "then":
            premise_compound = "if " + premise_compound
        if hypothesis_conjunction == "then":
            hypothesis_compound = "if " + hypothesis_compound
        result.append((premise_compound, "entails", hypothesis_compound, [(simple1_encoding, pcore, pcore2), (simple2_encoding, hcore, hcore2), (encoding,)]))
    return result

def generate_balanced_simple_data(simple_filename, boolean_filename, simple_size, boolean_size, data, restrictions=[1000000]*19):
    e,c,p = split_dict(simple_filename, restrictions)
    ekeys = list(e.keys())
    ckeys = list(c.keys())
    pkeys = list(p.keys())
    label_size = int(size/3)
    examples = []
    for i in range(label_size):
        encoding = json.loads(random.choice(ekeys))
        premise, hypothesis = encoding_to_example(data,encoding,"entails")
        examples.append((premise.string, "entails", hypothesis.string, [encoding]))
    for i in range(label_size):
        encoding = json.loads(random.choice(ckeys))
        premise, hypothesis = encoding_to_example(data,encoding)
        examples.append((premise.string, "contradicts", hypothesis.string, [encoding]))
    for i in range(label_size):
        encoding = json.loads(random.choice(pkeys))
        premise, hypothesis = encoding_to_example(data,encoding)
        examples.append((premise.string, "permits", hypothesis.string, [encoding]))
    bool_label_size = int(boolean_size/3)
    bool_e,bool_c,bool_p = bool_split_dict(filename, [100000]*19)
    bool_ekeys = list(bool_e.keys())
    bool_ckeys = list(bool_c.keys())
    bool_pkeys = list(bool_p.keys())
    examples += generate_boolean_data(bool_ekeys, ekeys, ckeys, pkeys, bool_label_size, data)
    examples += generate_boolean_data(bool_ckeys, ekeys, ckeys, pkeys, bool_label_size, data)
    examples += generate_boolean_data(bool_pkeys, ekeys, ckeys, pkeys, bool_label_size, data)
    random.shuffle(examples)
    return examples

if __name__ == "__main__":
    #encodings.append([pindex, hindex, porder, horder,first_relation, second_relation])
    build_simple_file()
    build_boolean_file()
    data, _, _ = process_data(1.0)
    check_data(data)

    cores = get_cores(data)
    size = 2000000
    examples = generate_balanced_data("big_data.pkl", "boolean_data.pkl",6,50 , cores, data)
    save_data(examples[:int(size*0.9)], "simplejoint.train")
    save_data(examples[int(size*0.9):int(size*0.95)], "simplejoint.val")
    save_data(examples[int(size*0.95):], "simplejoint.test")
    train_data, val_data, test_data = process_data(0.6)
    train_cores = get_cores(train_data)
    val_cores = get_cores(val_data)
    test_cores = get_cores(test_data)
    size = 2000000
    train_examples = generate_balanced_data("big_data.pkl","boolean_data.pkl",2000000, 0, cores, train_data)
    val_examples = generate_balanced_data("big_data.pkl","boolean_data.pkl",2000000, 0, cores, val_data)
    test_examples = generate_balanced_data("big_data.pkl","boolean_data.pkl",2000000, 0, cores, test_data)
    save_data(examples[:int(size*0.9)], "simpledisjoint.train")
    save_data(examples[int(size*0.9):int(size*0.95)], "simpledisjoint.val")
    save_data(examples[int(size*0.95):], "simpledisjoint.test")
