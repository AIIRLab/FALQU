import random
import xml.etree.cElementTree as ET
import html
import csv
import argparse

from Entity_Parser_Record.post_link_parser_record import PostLinkParserRecord
from Entity_Parser_Record.post_parser_record import PostParserRecord
from xml.dom import minidom
post = None
post_link = None


def generate_topic_xml(new_xml_file_path, dic_questions):
    # this method generates the XML files
    root = ET.Element("Topics")
    for question_id in dic_questions:
        sub = ET.SubElement(root, "Question")
        ET.SubElement(sub, "ID").text = str(question_id)
        title = dic_questions[question_id][0]
        title = html.unescape(title)
        body = dic_questions[question_id][1]
        body = html.unescape(body)
        ET.SubElement(sub, "TITLE").text = title
        ET.SubElement(sub, "BODY").text = body
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(new_xml_file_path, "w", encoding="utf-8",) as f:
        f.write(xml_str)


def generate_collection(new_xml_file_path, dic_answers):
    # this method generate the XML file for the collection that has answers posts
    root = ET.Element("Posts")
    for answer_id in dic_answers:
        sub = ET.SubElement(root, "DOC")
        ET.SubElement(sub, "DOCNO").text = str(answer_id)
        text = dic_answers[answer_id]
        text = html.unescape(text)
        ET.SubElement(sub, "TEXT").text = text
    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(new_xml_file_path, "w", encoding="utf-8",) as f:
        f.write(xml_str)


def generate_collection_file():
    # list of questions ids with duplicates
    lst_duplicates = get_duplicates()

    count = 0
    accepted_answer = 0
    dic_anwers = {}

    # for question_id in post.map_questions:
    #     if question_id in lst_duplicates:
    #         continue
    #     question = post.map_questions[question_id]
    #     count += 1
    #     if question.accepted_answer_id is not None:
    #         accepted_answer += 1

    # Selecting answers to be in the collection posts
    for answer_id in post.map_just_answers:
        answer = post.map_just_answers[answer_id]
        if answer.parent_id in lst_duplicates:
            continue
        else:
            dic_anwers[answer_id] = answer.body

    # Generating the XML file
    generate_collection("LawPosts.xml", dic_anwers)

    # print(accepted_answer)
    # print(count)
    # print(accepted_answer/count)
    # print(len(dic_anwers.keys()))


def get_duplicates():
    # This method detects the questions that have duplicates
    lst_duplicates = []
    for question_id in post_link.map_duplicate_posts:
        lst_duplicates.extend(post_link.map_duplicate_posts[question_id])
    return lst_duplicates


def generate_topic_files():
    # This method generated the XML files for the topics
    lst_duplicates = get_duplicates()
    question_scores = {}
    all_question_ids = []
    for question_id in post.map_questions:
        # Questions with duplicates are not considered
        if question_id in lst_duplicates:
            continue
        question = post.map_questions[question_id]
        # Questions with no accepted answer are not considered
        if question.accepted_answer_id is None:
            continue
        all_question_ids.append(question_id)
        if question.score in question_scores:
            question_scores[question.score].append(question_id)
        else:
            question_scores[question.score] = [question_id]
    # Generating test and training sets
    bins = {1000: []}
    for score in question_scores:
        if len(question_scores[score]) < 10:
            bins[1000].extend(question_scores[score])
        else:
            bins[score] = question_scores[score]
    test_question_ids = []
    for score in bins:
        temp = bins[score]
        random.seed(4)
        random.shuffle(temp)
        count = round(len(temp)*0.1)
        test_question_ids.extend(temp[:count])
    test_question_ids = test_question_ids[:-1]
    test = {}
    train = {}
    for question_id in test_question_ids:
        question = post.map_questions[question_id]
        test[question_id] = [question.title, question.body]
    for question_id in all_question_ids:
        if question_id in test:
            continue
        question = post.map_questions[question_id]
        train[question_id] = [question.title, question.body]
    generate_topic_xml("Topics/TestTopics.xml", test)
    generate_topic_xml("Topics/TrainTopics.xml", train)
    lst_question_ids_test = list(test.keys())
    lst_question_ids_train = list(train.keys())
    # print(len(test.keys()))
    # print(len(train.keys()))
    return lst_question_ids_test, lst_question_ids_train


def generate_qrel_files(lst_question_ids_test, lst_question_ids_train):
    # This method generates the qrel files
    file = open("Qrels/qrel_test.tsv", "w", newline='')
    writer = csv.writer(file, delimiter='\t', lineterminator='\n')

    for question_id in lst_question_ids_test:
        writer.writerow([str(question_id), "0", str(post.map_questions[question_id].accepted_answer_id), "1"])
    file.close()

    file = open("Qrels/qrel_train.tsv", "w", newline='')
    writer = csv.writer(file, delimiter='\t', lineterminator='\n')
    for question_id in lst_question_ids_train:
        writer.writerow([str(question_id), "0", str(post.map_questions[question_id].accepted_answer_id), "1"])
    file.close()

# temp1 = "C:/Users/Behrooz/Desktop/law.meta.stackexchange.com/Posts.xml"
# temp2 = "C:/Users/Behrooz/Desktop/law.meta.stackexchange.com/PostLinks.xml"


def main():
    global post
    global post_link
    parser = argparse.ArgumentParser(description='Generate test collection files')
    parser.add_argument('-p', type=str, required=True, dest='posts_file', help='path to Posts.xml')
    parser.add_argument('-l', type=str, required=True, dest='post_links_file', help='path to PostLinks.xml')

    args = parser.parse_args()

    print("reading LawSE files")
    post = PostParserRecord(args.posts_file)
    post_link = PostLinkParserRecord(args.post_links_file)

    # Generating the XML file for the collection LawPosts.xml
    print("Generating Collection file")
    generate_collection_file()
    # Generating the topics XML files
    print("Generating Topic files")
    lst_question_ids_test, lst_question_ids_train = generate_topic_files()
    # Generating the qrel files for training and test sets
    print("Generating qrel files")
    generate_qrel_files(lst_question_ids_test, lst_question_ids_train)


if __name__ == '__main__':
    main()