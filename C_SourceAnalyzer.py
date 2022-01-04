'''
Created on 2018/12/27
@author: Udagawa Tomohiro
2019/1/7
　定義名抽出    #define
　列挙体名抽出  typedef enum { }　,　enum  { }
　構造体名抽出 typedef　struct { } , struct { }
　上記抽出に対応
2019/1/8
　Pythonパッケージを使用せずに動作するように対応
　SorceAnalyzer_result.txtに出力結果を追加
2019/1/9
　typedef unionに対応
2019/1/10
　enumバグ対応
2019/1/14
　unionのバグに対応(｛｝間の｝による名前抽出失敗バグ)
　tableに対応
2019/1/23
　define  ****() ()は削除
2019/1/30
　func名を抽出可能
2019/2/5
　トレーサビリティ対応("TraceabilityID:"と"Covers:"を抽出)
　構造体リネーム検出対応 　typedef struct old_name new_name;
2019/2/14
　define \tによって検出できないdefine名を抽出
　下位フォルダも検索可能に倒した
2019/3/14
　関数名（の前にスペースが複数在ると検出できない問題を解消
2019/4/12
　To call function　リスト列挙
　関数ごとに呼ばれる関数をjsonファイルにリストアップ
2019/4/25
　call from function　リスト列挙
　指定解析フォルダ内に定義された関数がどの関数から呼ばれるのかリストアップ
2019/5/25
　global変数をリストアップ
2019/5/30
　define,structureをリストアップ
2019/6/4
　global変数のinput/output解析機能追加
2019/6/5
　関数のargument解析
2019/6/6
'''
import sys
import tkinter
import os
import re
import json
import pprint
import codecs

PATH=""
JSON_FLAG="enable"

path_w = 'SourceAnalyzer_result.txt'
skip_temp_flag = 0
#folder_path = "Nothing"#解析開始位置
cpath = "result.json"

func_list = []
func_cnt_list = []
#func_dic = {}
doc_dic = {}

def comm_skip(line):
    flag = -1
    global skip_temp_flag
    if(skip_temp_flag == 1):
        if(line.find("*/") > -1):
            skip_temp_flag = 0
        flag = 0 #0ならskip
    elif(line.find("/*") > -1):
        skip_temp_flag = 1
        if(line.find("*/") > -1):
            skip_temp_flag = 0
        flag = line.find("/*")
    elif(line.find("*/") > -1):
        flag = 0
    elif(line.find("//") > -1):
        flag = line.find("//")#0ならskip　0以上ならそれまでの文字列を検索可能
        
    return flag

def global_var_analyze(file_path):

    global doc_dic
    c_file_path = file_path[file_path.rfind("\\")+1:]

    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
    out_file = open(path_w,'a')
    text = "======== global variable analyze ========"
    print(text)
    out_file.write(text + "\n")
    cnt = 0
    flag = 0
    brc_cnt = 0
    #temp_flg = 0
    equal_cnt = 0# ”=”があった行
    equal_flag = 0# ”=”があった行
    skp_bksl_flag = False
    temp_line=""
    
    for line in file_data:
        cnt += 1
        line = line[:line.find("\n")]
        line = line.expandtabs()#tabを空白に変換
        line = re.sub(r"\s+", " ", line)#複数ある空白を空白ひとつに変更

        if( comm_skip(line) > -1):
            skip_flag = comm_skip(line)
            if(skip_flag == 0): 
                continue
            elif(skip_flag > 0):
                line = line[:comm_skip(line)]
        if(re.search( r'\s*#define' , line ) != None):#define行に関数はないのでSKIP
            if( line.find("\\") > -1 ):
                skp_bksl_flag = True
            continue
        
        if(skp_bksl_flag == True):#?
            skp_bksl_flag = False
            if( line.find("\\") > -1 ):
                skp_bksl_flag = True
            continue

        if(line.find("{") > -1):
            brc_cnt += line.count("{")
            if brc_cnt == 1:# 1の場合のみ
                temp_line = line

        if(line.find("}") > -1):
            brc_cnt -= line.count("}")
            # temp_flg = 1#最後の閉じタグの判定"}"
            if brc_cnt == 0:
                line = temp_line

        if(brc_cnt == 0):
            if(line.find("=") > -1):
                equal_flag = 1
                equal_line = line
                #temp_line_flag = 1
                equal_cnt = cnt

        text = str(cnt)+"\t"+str(brc_cnt)                
        
        if(brc_cnt == 0 and equal_flag == 1):# "{","}" がカウントが"±0"で、且つ、最後が"}"の場合
            #equal_flag = 0
            flag = 1
        else:
            continue
        
        if flag == 1:#
            if(equal_cnt < cnt):#改行されている場合
            #    text = "brc_cnt\t = "+str(brc_cnt)
            #    print(text)
            #    out_file.write(text + "\n")
                line = equal_line
                if(line.find(" =") > -1):
                    line = line[:line.find(" =")]
                if(line.find("=") > -1):
                    line = line[:line.find("=")]

                if(line.rfind(" [") > -1):
                    line = line[:line.rfind(" [")]
                if(line.rfind("[") > -1):
                    line = line[:line.rfind("[")]
                
                if(line.rfind(" ") > -1):
                    line = line[line.rfind(" ")+1:]
                    #text = str(cnt) + "\t" + line
                    text = line
                    print(text)
                    out_file.write(text + "\n")
                    doc_dic[c_file_path].setdefault("global variable", {})
                    doc_dic[c_file_path]["global variable"].setdefault(text, "Null")

                equal_flag = 0
                flag = 0
            if(equal_cnt == cnt): #改行を含まない変数はこれでたいてい取れる
                #global_pat = r'(\{\w)?\}?\W(;$)'
                #if(re.search( global_pat , line ) != None):
                    if(line.find(");") == -1):#関数みたいなやつ プロトタイプが取れてしまう。
                        #if(line.find("return") == -1):#returnがなければ
                        if(line.find(" =") > -1):
                            line = line[:line.find(" =")]
                        if(line.find("=") > -1):
                            line = line[:line.find("=")]

                        if(line.rfind(" [") > -1):
                            line = line[:line.rfind(" [")]
                        if(line.rfind("[") > -1):
                            line = line[:line.rfind("[")]

                        if(line.rfind(" ") > -1):
                            line = line[line.rfind(" ")+1:]

                        #text = str(cnt) + "\t" + line
                        text = line
                        print(text)
                        out_file.write(text + "\n")
                        doc_dic[c_file_path].setdefault("global variable", {})
                        doc_dic[c_file_path]["global variable"].setdefault(text, "Null")
                    equal_flag = 0
                    flag = 0
    file_data.close()
    out_file.close()

def fnc_arg_io_analyze(file_path):
    global func_cnt_list
    in_flag     = False
    out_flag    = False
    io_flag     = False
    flag        = False

    c_file_path = file_path[file_path.rfind("\\")+1:]
    out_file = open(path_w,'a')
    text = "======== function argument I/O analyze ========"
    print(text)
    out_file.write(text + "\n")
    
    cnt = 0
    #flag = 0
    brc_cnt = 0
    #temp_flg = 0
    equal_cnt = 0# ”=”があった行
    equal_flag = 0# ”=”があった行
    skp_bksl_flag = False
    
    if(doc_dic[c_file_path].get("function")):
        for target_func in doc_dic[c_file_path]["function"]:
            text = target_func
            print(text)
            out_file.write(text + "\n")

            if(doc_dic[c_file_path]["function"][target_func].get("argument")):
                for target_arg in doc_dic[c_file_path]["function"][target_func]["argument"]:
                    text = "target_arg:\t" + target_arg
                    print(text)
                    out_file.write(text + "\n")
                    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
                    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
                    for line in file_data:
                        cnt += 1
                        line = line[:line.find("\n")]
                        line = line.expandtabs()#tabを空白に変換
                        line = re.sub(r"\s+", " ", line)#複数ある空白を空白ひとつに変更

                        #コメントスキップ
                        if( comm_skip(line) > -1):
                            skip_flag = comm_skip(line)
                            if(skip_flag == 0):
                                continue
                            elif(skip_flag > 0):
                                line = line[:comm_skip(line)]
        
                        if(skp_bksl_flag == True):#?
                            skp_bksl_flag = False
                            if( line.find("\\") > -1 ):
                                skp_bksl_flag = True
                            continue

                        if(line.find("{") > -1):
                            brc_cnt += line.count("{")
                            if brc_cnt == 1:# 1の場合のみ
                                temp_line = line

                        if(line.find("}") > -1):
                            brc_cnt -= line.count("}")
                            temp_flg = 1#最後の閉じタグの判定"}"
                            if brc_cnt == 0:
                                line = temp_line

                        if(brc_cnt == 0):
                            if(line.find("=") > -1):
                                equal_flag = 1
                                equal_line = line
                                #temp_line_flag = 1
                                equal_cnt = cnt
                        
                        if(line.find(target_arg) > -1):
                            text = "\t\t"+line
                            print(text)
                            out_file.write(text + "\n")

                    file_data.close()
    
    out_file.close()
    #return flag

def global_var_io_analyze(file_path):
    global doc_dic
    global func_list
    global func_cnt_list
    cnt = 0

    c_file_path = file_path[file_path.rfind("\\")+1:]
    
    out_file = open(path_w,'a')
    text = "======== global variable I/O analyze ========"
    print(text)
    out_file.write(text + "\n")
    if(doc_dic[c_file_path].get("global variable")):
        input_cnt = 0
        output_cnt = 0
        func_num = 0

        for g_target in doc_dic[c_file_path]["global variable"]:
            text = "target:\t" + g_target
            print(text)
            out_file.write(text + "\n")
            #for func_num in range(len(func_list)):
            cnt = 0
            input_cnt = 0
            output_cnt = 0

            #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
            file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み

            for line in file_data:
                cnt += 1
                line = line[:line.find("\n")]
                line = line.expandtabs()#tabを空白に変換
                line = re.sub(r"\s+", " ", line)#複数ある空白を空白ひとつに変更

                if( comm_skip(line) > -1):
                    skip_flag = comm_skip(line)
                    if(skip_flag == 0):
                        continue
                    elif(skip_flag > 0):
                        line = line[:comm_skip(line)]
                
                #for i in range(len(func_cnt_list)):
                if(len(func_cnt_list) > 0):
                    if(func_cnt_list[func_num] == cnt):#関数行がきたら関数表示
                        text = func_list[func_num]
                        print(text)
                        out_file.write(text + "\n")
                    
                    elif(func_cnt_list[func_num] < cnt):
                        if( len(func_cnt_list) > func_num + 1 ):
                            if(func_cnt_list[func_num+1] == cnt):
                                func_num += 1
                                text = func_list[func_num]
                                print(text)
                                out_file.write(text + "\n")
                                continue
                                    
                        #if( line.find("&"+g_target)> -1):
                        #        continue

                        if( line.find(g_target)> -1):
                                
                                #text = "\t" + str(cnt)
                                #print(text)
                                #out_file.write(text + "\t")
                                
                                target_pos = line.find(g_target)
                                if line.find("return")>-1:#
                                    continue
                                if line.find("while")>-1:#
                                    if(line.find("while")+6 <= target_pos):
                                        input_cnt += 1
                                        text =  "\t" + str(cnt) + "\tinput\t(while)\t"+ line
                                    else:
                                        text = "\t" + str(cnt) + "\t!!!!! NG while case !!!!!\t"+ line
                                    print("\t" + text)
                                    out_file.write("\t" + text + "\n")
                                elif line.find("for")>-1:#
                                    if(line.find("for")+4 <= target_pos):
                                        input_cnt += 1
                                        text = "\t" + str(cnt) + "\tinput\t(for)\t"+ line
                                    else:
                                        text = "\t" + str(cnt) + "\t!!!!! NG for case !!!!!\t"+ line
                                    print("\t" + text)
                                    out_file.write("\t" + text + "\n")
                                elif line.find("if")>-1:#
                                    if(line.find("if")+3 <= target_pos):
                                        input_cnt += 1
                                        text = "\t" + str(cnt) + "\tinput\t(if)\t"+ line
                                    else:
                                        text = "\t" + str(cnt) + "\t!!!!! NG if case !!!!!\t"+ line
                                    print("\t" + text)
                                    out_file.write("\t" + text + "\n")
                                elif line.find("memset")>-1:#
                                    if(line.find("memset")+7 < target_pos):
                                        output_cnt += 1
                                        text = "\t" + str(cnt) + "\toutput\t(memset)\t"+ line
                                    else:
                                        text = "\t" + str(cnt) + "\t!!!!! NG memset case !!!!!\t"+ line
                                    print("\t" + text)
                                    out_file.write("\t" + text + "\n")
                                    
                                elif line.find("=")>-1:#
                                    if(line.find("=")+1 > target_pos):
                                        output_cnt += 1
                                        text = "\t" + str(cnt) + "\toutput\t(=)\t"+ line
                                        if(doc_dic[c_file_path]["function"][func_list[func_num]].get("to call function")):
                                            for func_name in doc_dic[c_file_path]["function"][func_list[func_num]]["to call function"]:
                                                if(line.find(func_name)>-1):
                                                    if(line.find(func_name) < target_pos):
                                                        text = "\t" + str(cnt) + "\tunknown\t(func)\t"+ line                                   
                                    elif(doc_dic[c_file_path]["function"][func_list[func_num]].get("to call function")):
                                        if(line.find("=") < target_pos):
                                            input_cnt += 1
                                            text = "\t" + str(cnt) + "\tinput \t(=)\t"+ line
                                        for func_name in doc_dic[c_file_path]["function"][func_list[func_num]]["to call function"]:
                                            if(line.find(func_name)>-1):
                                                if(line.find(func_name) < target_pos):
                                                    text = "\t" + str(cnt) + "\tunknown\t(func)\t"+ line
                                                elif(line.find(func_name) > target_pos):
                                                    output_cnt += 1
                                                    text = "\t" + str(cnt) + "\toutput\t(func)\t"+ line
                                    print("\t" + text)
                                    out_file.write("\t" + text + "\n")
                                else:
                                    text = "\t" + str(cnt) + "\tunknown\t(func)\t"+ line
                                    print("\t" + text)
                                    out_file.write("\t" + text + "\n")

            file_data.close()

    #for i in range(len(func_cnt_list)):
    #    print(func_cnt_list[i])
    out_file.close()

def objtag_analyze(file_path):
    cnt = 0
    flag = 0
    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
    out_file = open(path_w,'a')
    text = "======== objct_id analyze ========"
    print(text)
    out_file.write(text + "\n")
    obj_tag_list = []
    
    func_cnt = 0
    for line in file_data:
        cnt += 1
        line = line[:line.find("\n")]
        
        if len(func_cnt_list) > func_cnt:
            if(func_cnt_list[func_cnt] == cnt):
                text = "\t" + line
                print(text)                 #関数表示
                out_file.write(text + "\n") #関数表示
                func_cnt += 1 
        
        if( line.find("/*") > -1 and line.find("*/") > -1 ):
            line = line[line.find("/*")+2:line.find("*/")]
            flag = 1
        else:
            flag = 0
            continue
        
        if flag == 1:
            if(line.find("[") > -1 and line.find("]") > -1 ):
                flag = 2
            else:
                flag = 0
                continue
        else:
            flag = 0
            continue
        
        if flag == 2:
            if line.find("[") > -1 :
                line = line[line.find("["):line.find("]")+1]
                #text = str(cnt) + "\t" + line
                if len(line) < 8:
                    flag = 0
                    continue
                text = line
                obj_tag_list.append(text)
                    
                tag_cnt = 0 #初期化
                for i in range( len(obj_tag_list) ):
                    if( obj_tag_list[i] == text ):
                        tag_cnt += 1
                if(tag_cnt == 1):#正常ケース
                    #print( text )                 #タグ表示
                    pass
                else:
                    #print( text + "\t Duplication!" + "\t cnt = " + str(tag_cnt) )
                    text = text + "\t Duplication!" + "\t cnt = " + str(tag_cnt)
                print(text)
                out_file.write(text + "\n") #タグ表示
            flag = 0
        else:
            flag = 0
            continue
    file_data.close()
    out_file.close()

def trc_analyze(file_path):
    cnt = 0
    flag = 0
    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
    out_file = open(path_w,'a')
    text = "======== traceablity analyze ========"
    print(text)
    out_file.write(text + "\n")
    
    func_cnt = 0
    for line in file_data:
        cnt += 1
        line = line[:line.find("\n")]
        
        if len(func_cnt_list) > func_cnt:
            if(func_cnt_list[func_cnt] == cnt):
                text = "\t" + line
                print(text)
                out_file.write(text + "\n")
                func_cnt += 1 
        if( line.find("/*") > -1 and line.find("*/") > -1 ):
            flag = 1
        else:
            flag = 0
            continue
        if flag == 1:
            if(line.find("TraceabilityID:") > -1 or line.find("Covers:") > -1 ):
                flag = 2
            else:
                continue
        else:
            flag = 0
            continue
        if flag == 2:
            if line.find("TraceabilityID:") > -1 :
                line = line[line.find("TraceabilityID:"):line.find("*/")]
            if line.find("Covers:") > -1 :
                line = line[line.find("Covers:"):line.find("*/")]
            text = str(cnt) + "\t" + line
            print(text)
            out_file.write(text + "\n")
            flag = 0
        else:
            flag = 0
            continue
    file_data.close()
    out_file.close()

def fnc_analyze(file_path):

    global doc_dic
    c_file_path = file_path[file_path.rfind("\\")+1:]
    global func_list
    global func_arg_list
    global pre_func_list
    global func_cnt_list
    
    func_list = []
    func_arg_list = []
    pre_func_list = []
    func_cnt_list = []

    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
    out_file = open(path_w,'a')#ファイル最下行に追加書き込み
    flag = 0
    text = "======== function analyze ========"
    print(text)
    out_file.write(text + "\n")
    #print(path)
    brc_cnt = 0
    mbrc_cnt = 0
    func_cnt = 0
    cnt = 0
    arg_brc_cnt = 0
    temp_flg = 0
    func_name = "None error"
    arg_flag = 0
    
    skp_bksl_flag = False
    for line in file_data:
        cnt += 1
        line = line[:line.find("\n")]
        line = line.expandtabs()
        line = re.sub(r"\s+", " ", line)#複数ある空白を空白ひとつに変更
        if( comm_skip(line) > -1):
            skip_flag = comm_skip(line)
            if(skip_flag == 0):
                continue
            elif(skip_flag > 0):
                line = line[:comm_skip(line)]
        if(re.search( r'\s*#define' , line ) != None):#define行に関数はないのでSKIP
            if( line.find("\\") > -1 ):
                skp_bksl_flag = True
            continue
        if(skp_bksl_flag == True):#?
            skp_bksl_flag = False
            if( line.find("\\") > -1 ):
                skp_bksl_flag = True
            continue
        
        if flag == 0 :#関数名抽出
            if(mbrc_cnt == 0):
                if(line.find("=") > -1):
                    continue
                if(line.find("(") > -1):#条件式がつくもの
                    if (line[0] == "#" or line.find("=") > -1):#for文skip
                        flag = 0
                        continue
                    #if (line.find("while") > -1):#while文skip
                    #    continue
                    bline = line[:line.find("(")]#テーブルをｓｋｉｐ
                    #print(bline)
                    if(bline.find("{") > -1 or bline.find("}") > -1):
                        continue
                    #if(re.search( r'\S' , bline ) == None):#"("の前に空白文字以外が存在しなければSKIP
                    #    continue
                    if(line.find("for") > -1):
                        continue
                    if(line.find("if") > -1):
                        continue
                    if(line.find("while") > -1):
                        continue
                    if(line.find("switch") > -1):
                        continue
                    if(line.find(")") > -1):#プロトタイプ関数やキャストをskip　
                        eline = line[line.find(")"):]
                        if(eline.find(";") > -1):
                            continue
                    else:
                        mbrc_cnt += line.count("(")
                        mbrc_cnt -= line.count(")")

                    flag = 1
                    
                    """
                    if(line.find("(") > -1):
                        arg_brc_cnt += line.count("(")
                    if(line.find(")") > -1):
                        arg_brc_cnt -= line.count(")")
                    """
                        
                    func_arg = line[line.find("("):line.rfind(")")+1]#引数 argument analyze

                    if(mbrc_cnt > 0):
                        func_arg = line[line.rfind("("):]

                    """
                    if(arg_brc_cnt == 0 and arg_flag == 0):
                        func_arg = line[line.find("("):line.rfind(")")+1]#引数
                        #arg_flag = 0
                    elif(arg_brc_cnt > 0 and arg_flag == 0):
                        func_arg = line[line.rfind("("):]
                        arg_flag = 1
                    elif(arg_brc_cnt > 0 and arg_flag == 1):
                        func_arg = func_arg + line
                    elif(arg_brc_cnt == 0 and arg_flag == 1):
                        func_arg = func_arg + line
                        arg_flag = 0
                    """
                    if line.find(" (") > -1:
                        fnc_line = line[:line.find(" (")]

                    elif line.find("(") > -1:
                        fnc_line = line[:line.find("(")]

                    func_name = fnc_line[fnc_line.rfind(" ")+1:]

                    func_cnt = cnt#関数らしきものが合ったら記録しとく
                    if(mbrc_cnt != 0):
                        flag = 0
                        continue
            else:#引数宣言が改行されているケース brc_cntが0以上
                mbrc_cnt += line.count("(")
                mbrc_cnt -= line.count(")")
                if(mbrc_cnt == 0):
                    flag = 1
                    eline = line[line.rfind(")"):]
                    func_arg = func_arg + line
                    if(eline.find(";") > -1):
                        flag = 0
                        continue
                else:
                    func_arg = func_arg + line

        if flag == 1:#関数の中括弧終了タグを探索

            if(line.find("{") > -1):
                brc_cnt += line.count("{")
                #temp_flg = 1#brc_cntが0でflag2のケースへの遷移防止
            if(line.find("}") > -1):
                brc_cnt -= line.count("}")
                temp_flg = 1#brc_cntが0でflag2のケースへの遷移防止
            if(brc_cnt == 0 and temp_flg == 1):
                flag = 2
            else:
                temp_flg = 0
                continue

        if flag == 2 :
        #if flag > 2:
            #print(line + "\t" + str(cnt))
            if(func_cnt == 0):#一個も関数が見つかってない場合にエラー解析用
                func_cnt = cnt
            text = func_name + "\t" + str(func_cnt)
            print(text)
            out_file.write(text + "\n")
            func_list.append(func_name)
            func_cnt_list.append(func_cnt)
            func_arg_list.append(func_arg)
            func_arg = []  #func_arg初期化

            #以下は初期化
            func_name = "None error"
            func_cnt = 0
            flag = 0
            temp_flg = 0
    for i in range(len(func_list)):
        doc_dic[c_file_path].setdefault("function", {})
        doc_dic[c_file_path]["function"].setdefault(func_list[i], {})
        doc_dic[c_file_path]["function"][func_list[i]].setdefault("raw argument",func_arg_list[i])
        #doc_dic[c_file_path]["function"][func_list[i]].setdefault(func_arg_list[i], {})

    text = "--- NUMBER OF FUNCTION ==> " + "\t\t\t" + str(len(func_list)) + "\t---"
    print(text)
    out_file.write(text + "\n")
    file_data.close()
    out_file.close()
    return func_list

def to_call_func_analyze(file_path):
    global func_list
    global func_cnt_list
    #global func_dic
    
    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
    out_file = open(path_w,'a')#ファイル最下行に追加書き込み
    text = "======== to call function analyze ========"
    print(text)
    out_file.write(text + "\n")
    cnt = 0
    func_cnt = len(func_list)
    func_pos = 0

    c_file_path = file_path[file_path.rfind("\\")+1:]
    #doc_dic.setdefault(c_file_path, {})
    #func_dic.setdefault(c_file_path, {})
    #func_dic[func_list[func_pos]].setdefault(text,"Null")

    for line in file_data:
        cnt += 1
        line = line[:line.find("\n")]
        line = line.expandtabs()
        line = re.sub(r"\s+", " ", line)#複数ある空白を空白ひとつに変更
        if( comm_skip(line) > -1):
            skip_flag = comm_skip(line)
            if(skip_flag == 0):
                continue
            elif(skip_flag > 0):
                line = line[:comm_skip(line)]
        if(func_cnt > 0):
            if cnt > func_cnt_list[func_pos]:
                if line.find("for") > -1:
                    continue
                elif line.find("if") > -1:
                    continue
                elif line.find("else") > -1:
                    continue
                elif(line.find("while") > -1):
                    continue
                elif(line.find("switch") > -1):
                    continue
                if(line.find("(void)") > -1):
                    cur = line.find("(void)")
                    line = line[:cur-1] + line[cur+6:]
                if line.rfind(");") > -1:
                    cline = line[:line.find("(")]
                    ccline = line[:line.find("(")+1]
                    if ccline.find(" (") > -1:
                        cline = line[:line.find(" (")]
                    cline = cline[cline.rfind("=")+1:]
                    text = cline[cline.rfind(" ")+1:]
                    if( len(text) <= 1 ):
                        continue

                    #辞書
                    doc_dic[c_file_path]["function"][func_list[func_pos]].setdefault("to call function",{})
                    doc_dic[c_file_path]["function"][func_list[func_pos]]["to call function"].setdefault(text,"Null")

            if func_cnt > 1:
                if cnt == func_cnt_list[func_pos+1]:

                    func_cnt -= 1
                    func_pos += 1

    #pprint.pprint(func_dic[c_file_path], depth=3, width=40)
    """
    for source_key in doc_dic.keys():#ソース指定
        if(source_key == c_file_path):
            text = source_key
            print(text)
            out_file.write(text + "\n")
            if(doc_dic[source_key].get("function")):
                text = "\tfunction"
                print(text)
                out_file.write(text + "\n")
                func_key_dic = doc_dic[source_key]["function"]
                for func_key in func_key_dic.keys():#関数指定
                    text = "\t\t" + func_key
                    print(text)
                    out_file.write(text + "\n")
                    call_func_key_dic = func_key_dic[func_key]
                    for to_callfunc_key in call_func_key_dic.keys():#call関数指定
                        text = "\t\t\t" + to_callfunc_key
                        print(text)
                        out_file.write(text + "\n")
                        to_callfunc_key_dic = call_func_key_dic[to_callfunc_key]
                        for call_func_key in to_callfunc_key_dic.keys():#call関数指定
                            text = "\t\t\t\t" + call_func_key
                            print(text)
                            out_file.write(text + "\n")
    """
    #out_file.write(pprint.pformat(func_dic[c_file_path], depth=3, width=40))
    #out_file.write("\n")
    file_data.close()
    out_file.close()

def get_dict():
    return doc_dic

#json 書き込み 全処理終わってから
def write_json():
    global cpath#analyzerソースの位置
    global doc_dic

    text = "======== write result json ========"
    print(text)

    call_from_func_analyze()#コール先関数の全解析

    jsf = open( cpath , "w" )
    json.dump( doc_dic , jsf, indent = 4)
    #dmp = json.dumps(func_dic,jsf,ensure_ascii=False)
    #jsf.write(dmp)
    jsf.close()

def fnc_arg_analyze(file_path):
    global doc_dic
    global func_list
    global func_arg_list
    c_file_path = file_path[file_path.rfind("\\")+1:]
    out_file = open(path_w,'a')#ファイル最下行に追加書き込み
    text = "======== function argument analyze ========"
    print(text)
    out_file.write(text+"\n")

    arg_list=[]

    if( doc_dic[c_file_path].get("function") ):
        func_key_dic = doc_dic[c_file_path]["function"]
        for func_key in func_key_dic.keys():#調査関数指定
            arg_list=[]#初期化
            #if(doc_dic[c_file_path]["function"][func_key].get("function"))
            arg_line = doc_dic[c_file_path]["function"][func_key]["raw argument"]
            if(arg_line.find(" )") > -1):
                arg_line = arg_line[arg_line.find("(")+1:arg_line.rfind(" )")]
            else:
                arg_line = arg_line[arg_line.find("(")+1:arg_line.rfind(")")]

            text = func_key + "\t" +'"'+ arg_line +'"' + "\t" + str(arg_line.count(","))
            print(text)
            out_file.write(text + "\n")
            
            if(arg_line.find(",") > -1):
                for i in range(0,arg_line.count(",")+1):
                    arg = arg_line[arg_line.rfind(" ")+1:]
                    arg_list.append(arg)
                    if(arg_line.count(",") > -1):
                        arg_line = arg_line[:arg_line.rfind(",")]
                    elif(arg_line.count(" ,") > -1):
                        arg_line = arg_line[:arg_line.rfind(" ,")]
                    if( arg == "void" ):
                        arg = "None"
                    text = arg
                    print(text)
                    out_file.write(text + "\n")
            else:
                text = "1 arg"
                arg = arg_line[arg_line.rfind(" ")+1:]
                if( arg == "void" ):
                    arg = "None"
                arg_list.append(arg)
                text = arg

                print(text)
                out_file.write(text + "\n")

            for j in range(len(arg_list)-1,-1,-1):
                if(arg_list[j] != "None"):
                    doc_dic[c_file_path]["function"][func_key].setdefault("argument",{})
                    doc_dic[c_file_path]["function"][func_key]["argument"].setdefault(arg_list[j],{})

    out_file.close()            

def call_from_func_analyze():
    global doc_dic

    for source_key in doc_dic.keys():#ソース指定
        if( doc_dic[source_key].get("function") ):
            func_key_dic = doc_dic[source_key]["function"]
            for func_key in func_key_dic.keys():#調査関数指定
                for resource_key in doc_dic.keys():#ソース指定
                    if( doc_dic[resource_key].get("function") ):
                        refunc_key_dic = doc_dic[resource_key]["function"]
                        for refunc_key in refunc_key_dic.keys():#関数指定
                            if( refunc_key_dic[refunc_key].get("to call function") ):
                                call_func_key_dic = refunc_key_dic[refunc_key]
                                to_callfunc_key_dic = call_func_key_dic["to call function"]
                                for recall_func_key in to_callfunc_key_dic.keys():#call関数指定
                                    if( func_key == recall_func_key or func_key == "*"+recall_func_key):
                                    #if( func_key.find(recall_func_key) > -1 ):
                                        doc_dic[source_key]["function"][func_key].setdefault("call from function",{})
                                        doc_dic[source_key]["function"][func_key]["call from function"].setdefault(refunc_key,"Null")
    text = "======== call from function analyze ========"
    print(text)
    for source_key in doc_dic.keys():#ソース指定
        if( doc_dic[source_key].get("function") ):
            func_key_dic = doc_dic[source_key]["function"] 
            for func_key in func_key_dic.keys():#調査関数指定
                if( func_key_dic[func_key].get("call from function") ):
                    pass
                else:
                    text= func_key + ": Not called by anyone"
                    print(text)


def def_analyze(file_path):
    global doc_dic
    c_file_path = file_path[file_path.rfind("\\")+1:]
    
    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
    out_file = open(path_w,'a')
    text = "======== define analyze ========"
    print(text)
    out_file.write(text + "\n")
    cnt = 0

    for line in file_data:
        cnt += 1#行数計算
        line = line[:line.find("\n")]
        line = line.expandtabs()
        line = re.sub(r"\s+", " ", line)#複数ある空白を空白ひとつに変更
        if( comm_skip(line) > -1):
            skip_flag = comm_skip(line)
            if(skip_flag == 0):
                continue
            elif(skip_flag > 0):
                line = line[:comm_skip(line)]
        
        if(re.search( r'\s*#define' , line ) != None):
            #print("detect name of define!")
            #print(str(cnt) + "\t"+ line)
            define_line = line.find("#define ")
            define_line = line[define_line + 8:]

            if(define_line.find(" ") > -1):
                define_line = define_line[:define_line.find(" ")]
                doc_dic[c_file_path].setdefault("define",{})    
                doc_dic[c_file_path]["define"].setdefault(define_line,"Null")
                text = define_line  + "\t" + "line = " + str(cnt)
                print(text)
                out_file.write(text + "\n")

            elif(define_line.find("\t") > -1):
                print(define_line.find("\t"))
                define_line = define_line[:define_line.find("\t")]
                doc_dic[c_file_path].setdefault("define",{})    
                doc_dic[c_file_path]["define"].setdefault(define_line,"Null")
                text = define_line  + "\t" + "line = " + str(cnt)
                print(text)
                out_file.write(text + "\n")

    file_data.close()
    out_file.close()

def str_analyze(file_path):
    global doc_dic
    c_file_path = file_path[file_path.rfind("\\")+1:]
    
    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
    out_file = open(path_w,'a')
    cnt = 0
    str_flag = 0
    brc_cnt = 0
    text = "======== structure analyze ========"
    print(text)
    out_file.write(text + "\n")
    for line in file_data:
        cnt += 1#行数計算
        
        if( comm_skip(line) > -1):
            if(comm_skip(line) == 0):
                continue
            elif(comm_skip(line) > 0):
                line = line[:comm_skip(line)]

        if( str_flag == 0):
            if(line.find("typedef struct") > -1):
                str_flag = 1
                if(line.find("{") > -1):
                    brc_cnt += 1
                elif(line.find(";") > -1):
                    str_line = line[line.find("typedef struct")+15:]
                    str_name = str_line[str_line.find(" ")+1:str_line.find(";")]
                    text = str_name + "\t" + "line = " + str(cnt)
                    print(text)
                    out_file.write(text + "\n")
                    doc_dic[c_file_path].setdefault("struct",{})    
                    doc_dic[c_file_path]["struct"].setdefault(str_name,"Null")
            else:
                if(line.find("struct") == 0):
                    str_flag = 2
                    null_char = line.find(" ")
                    str_name = line[null_char+1:]
                    str_name = str_name[:str_name.find(" ")]
                    text = str_name + "\t" + "line = " + str(cnt)
                    print(text)
                    out_file.write(text + "\n")
                    doc_dic[c_file_path].setdefault("struct",{})    
                    doc_dic[c_file_path]["struct"].setdefault(str_name,"Null")
                    
        else:
            if( str_flag == 1):
                str_line = line.find("{")#構造体始端
                if(str_line > -1):
                    brc_cnt += 1
                str_line = line.find("}")#構造体終端
                if(str_line > -1): #構造体発見判定
                    brc_cnt -= 1
                if(brc_cnt == 0):
                    str_flag = 0
                    if( line.find("} ") > -1):
                        str_line = line[line.find("} ")+2:line.find(";")]
                        text = str_line  + "\t" + "line = " + str(cnt)
                        print(text)
                        out_file.write(text + "\n")
                        doc_dic[c_file_path].setdefault("struct",{})    
                        doc_dic[c_file_path]["struct"].setdefault(str_line,"Null")

                    elif( line.find("}") > -1):
                        str_line = line[line.find("}")+1:line.find(";")]
                        text = str_line  + "\t" + "line = " + str(cnt)
                        print(text)
                        out_file.write(text + "\n")
                        doc_dic[c_file_path].setdefault("struct",{})    
                        doc_dic[c_file_path]["struct"].setdefault(str_line,"Null")

            if( str_flag == 2):
                str_flag = 0
    file_data.close()
    out_file.close()

def enm_analyze(file_path):
    global doc_dic
    c_file_path = file_path[file_path.rfind("\\")+1:]
    
    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
    out_file = open(path_w,'a')
    cnt = 0
    enum_flag = 0   # typedef enum {}***;の検出フラグ
    nenum_flag = 0  # enum {};の検出フラグ
    nenum_str = "noname enum"
    text = "======== enumration analyze ========"
    print(text)
    out_file.write(text + "\n")
    for line in file_data:
        cnt += 1#行数計算
        
        if( comm_skip(line) > -1):
            if(comm_skip(line) == 0):
                continue
            elif(comm_skip(line) > 0):
                line = line[:comm_skip(line)]

        if(enum_flag == 0 and nenum_flag == 0):
            
            if(line.find("typedef enum") > -1):
                    enum_line = line.find("typedef enum")
                    enum_flag = 1
            elif(line.find("enum") > -1): #"typedef enum"が発見できなかった場合
                    nenum_line = line.find("enum")
                    nenum_flag = 1
                    nenum_cnt = cnt
        else:
            if(enum_flag > 0):

                if(line.find("} ") > -1):
                    enum_flag = 0
                    enum_line = line[line.find("} ")+2:line.find(";")]
                    text = str(enum_line)  + "\t" + "line = " + str(cnt)
                    print(text)
                    out_file.write(text + "\n")
                    doc_dic[c_file_path].setdefault("enum",{})    
                    doc_dic[c_file_path]["enum"].setdefault(enum_line,"Null")
                    
                elif(line.find("}") > -1):
                    enum_flag = 0
                    enum_line = line[line.find("}")+1:line.find(";")] #ｅｎｕｍ名前取得
                    text = str(enum_line)  + "\t" + "line = " + str(cnt)
                    print(text)
                    out_file.write(text + "\n")
                    doc_dic[c_file_path].setdefault("enum",{})    
                    doc_dic[c_file_path]["enum"].setdefault(enum_line,"Null")

            if(nenum_flag > 0):
                if(line.find("}") > -1):
                    nenum_flag = 0
                    nenum_line_check = line.find("}")
                    if( line[line.find("}")+1] == ";" ):#無名enum
                        text = nenum_str  + "\t"  + "line = " +  str(nenum_cnt)
                        print(text)
                        out_file.write(text + "\n")
                        doc_dic[c_file_path].setdefault("enum",{})    
                        doc_dic[c_file_path]["enum"].setdefault(nenum_str,"Null")
                    #if(nenum_line_check > -1):
                    else:
                        nenum_line_check = line.find("}")
                        if(nenum_line_check > -1):
                            nenum_line = line[line.find("}")+1:line.find(";")]
                        nenum_line_check = line.find("} ")
                        if(nenum_line_check > -1):
                            nenum_line = line[line.find("} ")+2:line.find(";")]
                        text = nenum_line  + "\t" + "line = " + str(cnt)
                        print(text)
                        out_file.write(text + "\n")
                        doc_dic[c_file_path].setdefault("enum",{})    
                        doc_dic[c_file_path]["enum"].setdefault(nenum_line,"Null")            
    file_data.close()
    out_file.close()
    
def uni_analyze(file_path):
    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
    out_file = open(path_w,'a')
    cnt = 0#行数計算用　カウント初期化
    brc_cnt = 0
    text = "======== union analyze ========"
    print(text)
    out_file.write(text + "\n")
    
    uni_flag = 0 
    t_uni_flag = 0 
    for line in file_data:
        cnt += 1#行数計算
        
        if( comm_skip(line) > -1):
            if(comm_skip(line) == 0):
                continue
            elif(comm_skip(line) > 0):
                line = line[:comm_skip(line)]

        if( t_uni_flag == 0 and uni_flag == 0 ):
            t_uni_line = line.find("typedef union")
            if(t_uni_line > -1):
                #print("t_uni_line")
                t_uni_flag = 1 
            uni_line = line.find("union")
            if(uni_line > -1):
                #print("uni_line")
                uni_flag = 1 
        else:
            if(t_uni_flag == 1):
                str_line = line.find("{")#構造体始端
                if(str_line > -1):
                    brc_cnt += 1
                str_line = line.find("}")#構造体終端
                if(str_line > -1):#構造体発見判定
                    brc_cnt -= 1
                if(brc_cnt == 0):
                    t_uni_line = line.find("}")#enum　終端
                    if(t_uni_line > -1):
                        t_uni_flag = 0
                        if(line.find("}") > -1 ):
                            t_uni_line = line[line.find("}")+1:line.find(";")]
                            text = t_uni_line  + "\t" + "line = " + str(cnt)
                        if(line.find("} ") > -1 ):
                            t_uni_line = line[line.find("} ")+2:line.find(";")]
                            text = t_uni_line  + "\t" + "line = " + str(cnt)                    
                        print(text)
                        out_file.write(text + "\n")
            if(uni_flag == 1):
                uni_flag = 0
            #print("uni_line")
    file_data.close()
    out_file.close()

def tbl_analyze(file_path):
    #file_data = open(file_path, "r" ,encoding="utf-8_sig")#ファイル読み込み
    file_data = codecs.open(file_path, "r", "utf-8_sig" , "ignore")#ファイル読み込み
    out_file = open(path_w,'a')
    cnt = 0#行数計算用　カウント初期化
    text = "======== table analyze ========"
    print(text)
    out_file.write(text + "\n")
    for line in file_data:
        cnt += 1#行数計算
        
        if( comm_skip(line) > -1):
            if(comm_skip(line) == 0):
                continue
            elif(comm_skip(line) > 0):
                line = line[:comm_skip(line)]
        line = line[:line.find("\n")]
        if(line.find("for") > -1):
            continue
        if(line.find("if") > -1):
            continue
        if(line.find("else if") > -1):
            continue
        if(line.find("while") > -1):
            continue
        m = re.search(r'\[\w*\]\s*=',line)#　"\"は無視
        if (m != None):
            if(line.find(";") == -1):
                r_line = line[:line.find("[")]
                print(r_line[r_line.rfind(" ")+1:] + "\t" + "line = " + str(cnt))
    file_data.close()
    out_file.close()

def finish(file_path):
    out_file = open(path_w, mode='a')
    out_file.write("_______________________________________________________________________________")
    out_file.close()

def file_analyze(file_path):
    global doc_dic 
    file_path = file_path[file_path.rfind("\\")+1:]
    doc_dic.setdefault(file_path, {})

def analyzer(file_path):
    file_analyze(file_path)
    def_analyze(file_path)
    enm_analyze(file_path)
    str_analyze(file_path)
    uni_analyze(file_path)
    #tbl_analyze(file_path)

    if file_path.find(".c") > -1:
        global_var_analyze(file_path)
        fnc_analyze(file_path)
        #fnc_arg_analyze(file_path)      #fnc_analyze()が必須
        #fnc_arg_io_analyze(file_path)   #fnc_analyze(),fnc_arg_analyze()が必須
        # to_call_func_analyze(file_path) #fnc_analyze()が必須
        # call_from_func_analyze()        #fnc_analyze(),to_call_func_analyze()が必須
        # global_var_io_analyze(file_path)
        # objtag_analyze(file_path)
    # trc_analyze(file_path)

    finish(file_path)

def mining_folder(folder_path):
    file_path = []
    file_list = os.listdir(folder_path)#ファイルリスト取得
    file_cnt = len(file_list)
    
    #print(file_cnt)
    print("========== folder ========= ")
    #print("      " + folder_path)
    for j in range(0,file_cnt):
        #print(str(j) +"\t"+ file_list[j])
        print(folder_path + '\\' + file_list[j])
        file_name = folder_path + '\\' + file_list[j]
        file_path.append( file_name )
    print("========== folder ========= ")

    file_list = os.listdir(folder_path)#ファイルリスト取得
    file_cnt = len(file_list)
    out_file = open(path_w, mode='a')
    out_file.write("_______________________________________________________________________________")
    out_file.close()
    for i in range (0,file_cnt):
        print("_______________________________________________________________________________")
        print(file_path[i])
        out_file = open(path_w, mode='a')
        out_file.write("\n" + file_path[i] + "\n")#ファイル名書き込み
        out_file.close()

        if(file_path[i].find(".htm") > -1):
            continue 
        elif(file_path[i].find(".bak") > -1):
            continue 
        elif(file_path[i].find(".c") > -1):
            analyzer(file_path[i])
        elif(file_path[i].find(".h") > -1):
            analyzer(file_path[i])
        elif(os.path.isdir(file_path[i]) == True):
            #print("========== folder ========= ")
            #print("      " + file_path[i])
            #print("========== folder ========= ")
            mining_folder(file_path[i])
        else:
            print("========== extra ========= ")
            print("      " + file_path[i])
            print("========== extra ========= ")
            
    for i in range (0,file_cnt): 
        file_path.remove(folder_path + '\\' + file_list[i])
            #print(len(file_path)) #check finalize

chk_bln = []
def btn_click(event):
    print("click")
    bln=event.widget
    if(bln.get()==False):
        bln.set(True)
    else:
        bln.set(False)

    for i in range(len(chk_bln)):
        print(chk_bln[i].get())

def c_source_analyzer(path,JSON_FLG):
    global path_w
    global cpath
    global PATH
    PATH = path
    folder_path = PATH
    # tk = tkinter.Tk()
    # tk.title('C Source Analyzer')
    # tk.geometry('300x600')
    # hLabel = []             #ラベルのハンドルを格納します
    # hCheck = []             #チェックボックスのハンドルを格納します
    # CheckVal = []           #チェックボックスにチェックが入っているかどうかを格納します
    if(PATH == ""):
        print("_______________________________________________________________________________")
        print("　↓　Please input the analyze file folder path")

        folder_path = input()
    #path = os.getcwd()
    path_w = folder_path + "\\" + path_w
    cpath = folder_path + "\\" + cpath
    out_file = open( path_w, mode='w')
    out_file.close()
    file_path = []

    file_list = os.listdir(folder_path)#ファイルリスト取得
    file_cnt = len(file_list)
    for i in range (0,file_cnt):
        print(str(i) +"\t"+ file_list[i])
        file_path.append( folder_path + '\\' + file_list[i])
    
    """tkinter program"""
    #     chk_bln.append(tkinter.BooleanVar())#チェックボックスの値を決定
    #     chk_bln[i].set(False)#チェックボックスの値を決定
    #     cbo = tkinter.Checkbutton(tk, variable=chk_bln[i], text = file_list[i])
    #     cbo.place(x=20, y=20*i)
    #     cbo.bind("<ButtonRelease-1>",btn_click)
        #CheckVal.append(var)#チェックボックスの値を，リストに追加
        #hCheck.append(cbo)#チェックボックスのハンドルをリストに追加
    text_input="y"
    if(PATH == ""):
        print("Run program ? (y/n)")
        text_input = input("y")
        print(text_input)

    if(text_input=="y" or text_input=="Y" or text_input == ""):
        for i in range (0,file_cnt):
            print("_______________________________________________________________________________")
            print(file_path[i])
            out_file = open(path_w, mode='a')
            out_file.write("\n" + file_path[i] + "\n")
            out_file.close() 

            if(file_path[i].find(".htm") > -1):
                continue
            elif(file_path[i].find(".bak") > -1):
                continue
            elif(file_path[i].find(".c") > -1):
                analyzer(file_path[i])
            elif(file_path[i].find(".h") > -1):
                analyzer(file_path[i])
            elif(os.path.isdir(file_path[i]) == True):
                #print("========== folder ========= ")
                #print("      " + file_path[i])
                #print("========== folder ========= ")
                mining_folder(file_path[i])
            else:
                print("========== extra ========= ")
                print("      " + file_path[i])
                print("========== extra ========= ")
        for i in range (0,file_cnt): 
            file_path.remove(folder_path + '\\' + file_list[i])
        if(JSON_FLG == True):
            write_json()

    else:
        print("Exit")
        exit()

def cmd_args():
    args = sys.argv
    for arg in args:
        if(arg.find("path=") > -1):
            PATH=arg[arg.rfind("path="):]
        elif(arg.find("json=") > -1):
            line=arg[arg.rfind("json="):]
            if(line.find("enable") > -1):
                JSON_FLAG = True
            elif(line.find("disable") > -1):
                JSON_FLAG = False
            else:
                pass
        else:
            pass

if __name__ == "__main__":
    args = sys.argv
    c_source_analyzer(PATH,JSON_FLAG)
