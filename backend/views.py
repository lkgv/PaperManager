from django.http import JsonResponse
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from .utils import util
from .models import *
from .utils.PaperNode import *
import json
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt 
def user_register(request):
    """
    User register
    :param request: request
    :return: response{"error_num", "msg":message of error}
    """
    response = {}
    username = request.POST['username']
    password = request.POST['password']
    #email = request.POST['email']

    if Users.objects.filter(username=username):
        response["error_num"] = 1
        response["msg"] = "The user has been registered!"
    else:
        user = Users.objects.create(username=username, password=password,
                                    # email=email,
                                    email='aaa',
                                    classification_tree_root='root')
        response['error_num'] = 0
        response['msg'] = 'success'
    return JsonResponse(response)

@csrf_exempt 
def user_login(request):
    """
    User login
    :param request: request
    :return: response{"error_num", "msg":message of errors}
    """
    response = {}
    print('Resuqst ', request)
    print('post: ', request.POST.keys())
    username_ = request.POST['username']
    password_ = request.POST['password']
    user = Users.objects.filter(username=username_)
    print(user)
    if user is not None:
        if user[0].password == password_:
            response["error_num"] = 0
            response["msg"] = "success"
        else:
            response["error_num"] = 1
            response["msg"] = "user password is wrong"
    else:
        response["error_num"] = 1
        response["msg"] = "user does not exist"
    res = JsonResponse(response)

    if response['error_num'] == 0:
        res.set_cookie('username', username_, 360001)
    return res


@csrf_exempt 
def user_logout(request):
    """
    User logout
    :param request: request
    :return: logout success Json Response
    """
    logout(request)
    response = {"error_num": 0, "msg": "logout success"}
    res = JsonResponse(response)
    return res


def add_classification(request):
    """
    add node in the classification tree
    :param request: request
    :return: Json response{"error_num", "msg": message of the error}
    """
    response = {}
    username = request.POST["username"]
    father_name = request.POST["father_name"]
    new_name = request.POST["name"]
    father = ClassificationTree.objects.filter(username=username, name=father_name)
    exist = ClassificationTree.objects.filter(username=username, name=new_name)
    if father is None:
        response["error_num"] = 1
        response["msg"] = "the father node does not exist"
    elif exist is not None:
        response["error_num"] = 2
        response["msg"] = "the node name had existed"
    else:
        node = ClassificationTree.objects.create(username=username,
                                                 name=new_name,
                                                 father=father_name)
        response["error_num"] = 0
        response["msg"] = "success"
    res = JsonResponse(response)
    return res


def add_paper(request):
    """
    add paper in one node of the classification tre
    :param request: request
    :return: later add
    """
    response = {}
    username = request.POST["username"]
    title = request.POST["title"]
    authors = request.POST["author"]
    publish_time = request.POST["publish_time"]
    add_time = request.POST["add_time"]
    source = request.POST["source"]
    url = request.POST["url"]
    hash_code = request.POST["hash_code"]
    node_name = request.POST["node_name"]
    paper = Paper.objects.create(username=username, title=title,
                                 publish_time=publish_time,
                                 add_time=add_time, source=source,
                                 url=url, hash_code=hash_code,
                                 classification_tree_node=node_name)
    for au in authors:
        author = Author.objects.filter(first_name=au["first_name"],
                                       last_name=au["last_name"],
                                       email=au["email"])
        if author:
            paper.author.add(author[0])
        else:
            new_author = Author.objects.create(first_name=au["first_name"], last_name=au["last_name"],
                                               email=au["email"])
            paper.author.add(new_author)
    response["error_num"] = 0
    response["msg"] = "success"
    res = JsonResponse(response)
    Log.objects.create(username=username, paper_title=title,
                       log="add paper "+title+" in "+node_name)
    return res


def save_note(request):
    """
    add and change node for a paper
    :param request: request
    :return: later add
    """
    response = {}
    username = request.POST["username"]
    paper_title = request.POST["paper_title"]
    paper_page = request.POST["paper_page"]
    note_content = request.POST["content"]
    exist = Note.objects.filter(username=username, paper_title=paper_title, paper_page=paper_page)
    if exist:
        exist[0].delete()
        response["msg"] = "change note successfully"
    else:
        response["msg"] = "add note successfully"
    note = Note.objects.create(username=username,
                               paper_title=paper_title,
                               paper_page=paper_page,
                               content=note_content)
    response["error_num"] = 0
    res = JsonResponse(response)
    Log.objects.create(username=username, paper_title=paper_title,
                       log="add note in"+paper_title+" page"+paper_page)
    return res


def show_paper_detail(request):
    """
    show the paper detail
    :param request: request
    :return: response
    """
    response = {"error_num": 0, "msg": "success"}
    title = request.POST["title"]
    username = request.POST["username"]
    response["title"] = title
    paper = Paper.objects.filter(username=username, title=title)
    response["publish_time"] = paper[0].publish_time
    response["add_time"] = paper[0].add_time
    response["source"] = paper[0].source
    response["url"] = paper[0].url
    res = JsonResponse(response)
    return res


def read_paper(request):
    """
    read the paper
    :param request: request
    :return: response
    """
    response = {}
    username = request["username"]
    title = request["title"]
    notes = Note.objects.filter(username=username, paper_title=title)
    note = []
    for note_ex in notes:
        tmp = {"page": note_ex.paper_page, "content": note_ex.content}
        note.append(tmp)
    response["path"] = username+"/"+title
    response["note"] = note
    res = JsonResponse(response)
    Log.objects.create(username=username, paper_title=title,
                       log="read paper "+title)
    return res


def show_paper_of_the_node(request):
    """
    show the paper in the node
    :param request: request
    :return: response
    """
    response = {}
    username = request.POST["username"]
    node_name = request.POST["classification_node"]
    node = ClassificationTree.objects.get(username=username, name=node_name)
    papers = Paper.objects.filter(username=username, classification_tree_node=node)
    papers_title = []
    for paper in papers:
        papers_title.append(paper.title)
    response["papers_title"] = papers_title
    res = JsonResponse(response)
    return res


def find_son(username, node):
    """
    find the son node name of "node"
    :param username: username
    :param node: the node name
    :return: the son list
    """
    son_node = ClassificationTree.objects.filter(username=username, father=node)
    if son_node:
        son = []
        for son_node_ex in son_node:
            son_node_ex = son_node_ex.name
            tmp = {"name": son_node_ex, "son": []}
            tmp["son"] = find_son(username, tmp["name"])
            son.append(tmp)
        return son
    else:
        return []


def show_classification_tree(request):
    """
    show the classification tree
    :param request: request
    :return: response
    """
    username = request.POST["username"]
    user = Users.objects.get(username=username)
    root = user.classification_tree_root
    node = {"name": root, "son": find_son(username, root)}
    response = {"node": node}
    res = JsonResponse(response)
    return res


def find_son_paper(username, node_name):
    """
    find the papers in the son node of the node_name
    :param username: username
    :param node_name: the name of the node
    :return: the title of the papers
    """
    sons = ClassificationTree.objects.filter(username=username, father=node_name)
    paper_title = []
    if sons:
        for sons_ex in sons:
            papers = Paper.objects.filter(username=username, classification_tree_node=sons_ex.name)
            for paper in papers:
                paper_title.append(paper.title)
            paper_title.extend(find_son_paper(username, sons_ex.name))
    return paper_title


def show_paper_of_the_subtree(request):
    """
    show the paper list of the subtree
    :param request: request
    :return: the paper title in the subtree
    """
    username = request.POST["username"]
    node_name = request.POST["node_name"]
    papers = Paper.objects.filter(username=username, classification_tree_node=node_name)
    papers_title = []
    if papers:
        for paper in papers:
            papers_title.append(paper.title)
    papers_title.extend(find_son_paper(username, node_name))
    return papers_title


def getTagList(request):
    userId = request.GET.get("userId")
    currentPath = request.GET.get("currentPath")
    response = util.getTagList(userId, currentPath)
    return JsonResponse(response)


def getFileList(request):
    userId = request.GET.get("userId")
    currentPath = request.GET.get("currentPath")
    response = util.getFileList(userId, currentPath)
    return JsonResponse(response)

def SubTreePaperPack(request):
    userId = request.GET.get("userId")
    currentPath = request.GET.get("currentPath")
    tempDir = "../resource/temp"
    outputDir = "../resource/tags/"+userId+"/outputDir"
    outputpath = util.SubTreePack(currentPath, userId, tempDir, outputDir)
    return "http:/127.0.0.1:8080/backend/resource/tags/"+userId+"/"+outputpath

def paper_node_pack(request):
    pass
