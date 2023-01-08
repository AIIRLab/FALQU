# FALQU: Finding Answers to Legal Questions

FALQU is a test collection for legal information retrieval. 
Questions and answers were obtained from Law Stack Exchange, a Q\&A website for legal professionals, students, 
and others with experience or interest in law.

The Process of FALQU development is describe in the paper. This repo, provides the codes 
used for development of this test collection. 

## Generating Test Collection
### Law Stack Exchange
Law Stack Exchange is an online Q\&A website for legal domain. It contains variety of 
questions and corresponding answers. We have downloaded the raw data from the [Internet Archive](https://archive.org/).
The 08-Oct-2022 snapshot snapshot is used to build this test collection.

To regenerate the test collection files including the LawPosts.xml, QRELs and Topics run the following command:

```buildoutcfg
python generate_test_collection_files.py -p /path/to/Posts.xml -l /path/to/PostLinks.xml
```
 
 where the two parameters are the paths to Posts and PostLinks file from the Internet Archive.
## Baseline Systems
Codes for PyTerrier and Sentence-BERT baseline systems are in FalQU_Baseline_Systems.ipynb file.

