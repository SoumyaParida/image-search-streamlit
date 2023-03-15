from __future__ import print_function

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import pickle
from google.auth.transport.requests import Request
#from google_auth_oauthlib.flow import InstalledAppFlow

from getfilelistpy import getfilelist
from google.oauth2 import service_account

from oauth2client import file, client, tools

from httplib2 import Http

import streamlit as st
import templates
from PIL import Image

import os
from twilio.rest import Client

#client = Client(os.environ['AC2f38b621802a9918bbeecb783b2728f3'], os.environ['c8983bef7638feeb0d0d76700f5f544e'])
#account_sid = os.environ['TWILIO_ACCOUNT_SID']
#auth_token = os.environ['TWILIO_AUTH_TOKEN']

account_sid = "AC2f38b621802a9918bbeecb783b2728f3"
auth_token = "c8983bef7638feeb0d0d76700f5f544e"


client = Client(account_sid, auth_token)

SCOPES = ['https://www.googleapis.com/auth/drive']
showimglist = list()

import requests # request img from web
import shutil # save img locally

# Track an index for image, prev and next buttons.
if 'idx' not in st.session_state:
    st.session_state.idx = 0

def view_next():
    """Update idx, reset to zero if index is above max"""
    photos = showimglist
    next_index = st.session_state.idx + 1
    if next_index >= len(photos):
        next_index = 0
    st.session_state.idx = next_index


def view_previous():
    """Update idx, reset to max if index is below zero"""
    photos = showimglist
    prev_index = st.session_state.idx - 1
    if prev_index < 0:
        prev_index = len(photos) - 1
    st.session_state.idx = prev_index

def share_whatsapp():
    """Update idx, reset to max if index is below zero"""
    photos = showimglist
    index = st.session_state.idx
    imagepath = photos[index]
    imgid = imagepath.split("id=")[1]
    url = "https://drive.google.com/uc?export=download&id=" + imgid
    #print("url", url)
    res = requests.get(url, stream = True)
    file_name = os.path.dirname(os.path.abspath(__file__)) + "/test.jpg"
    if res.status_code == 200:
    	with open(file_name,'wb') as f:
    		shutil.copyfileobj(res.raw, f)
    		print('Image sucessfully Downloaded: ',file_name)
    else:
    	print('Image Couldn\'t be retrieved')
    print("file_name", file_name)
    from_whatsapp_number="whatsapp:+14155238886"
    to_whatsapp_number="whatsapp:+919937266747"
    message = client.messages.create(body='Ignore this..',
                       media_url=[file_name],
                       from_=from_whatsapp_number,
                       to=to_whatsapp_number)
    print(message.sid)
    os.remove(file_name)
    print("removed file successfully")



def showImages(filteredImages):
	try:
	    idx = 0 
	    while idx < len(filteredImages):
	        for _ in range(len(filteredImages)):
	            cols = st.columns(2)
	            for col_num in range(2):
	            	if idx <= len(filteredImages): 
	                    cols[col_num].image(filteredImages[idx], 
	                         width=225)
	                    if st.button('Say hello'):
	                    	st.write('Why hello there')
	                    idx+=1
	    return
	except:
	    pass
	    return


def showImagesnew(filteredImages):
	try:
		idx = 0
		while idx < len(filteredImages):
		    for _ in range(len(filteredImages)): 
		        cols = st.columns(2) 

		        cols[0].image(filteredImages[idx], width=225)
		        if cols[0].button('WhatsApp'):
		        	cols[0].write('Why hello there')
		        idx+=1
		        cols[1].image(filteredImages[idx], width=225)
		        if cols[1].button('WhatsApp'):
		        	cols[1].write('Why hello there')
		        idx+=1
		return
	except:
	    pass
	    return

def search():
	for image in imagefiles:
		for parameters in image:
			parentid = parameters.get('parents')
			#print("parentid", parentid)
			parameters['parentName'] = targetfolderlist.get(parentid)
			#print("parentName", parameters.get('parentName'))

def merge(list1, list2):
     
    merged_list = tuple(zip(list1, list2))
    return merged_list

def getFiles(foldername):
	creds = None
	if os.path.exists('token.pickle'):

	    # Read the token from the file and 
	    # store it in the variable creds
	    with open('token.pickle', 'rb') as token:
	        creds = pickle.load(token)

	if not creds or not creds.valid:

	    # If token is expired, it will be refreshed,
	    # else, we will request a new one.
	    if creds and creds.expired and creds.refresh_token:
	        creds.refresh(Request())
	    else:
	        flow = InstalledAppFlow.from_client_secrets_file(
	            'credentials.json', SCOPES)
	        creds = flow.run_local_server(port=0)

	    # Save the access token in token.pickle 
	    # file for future usage
	    with open('token.pickle', 'wb') as token:
	        pickle.dump(creds, token)

	# Connect to the API service
	drive = build('drive', 'v3', credentials=creds)

	# request a list of first N files or 
	# folders with name and id from the API.
	resource = drive.files()

	# First, get the folder ID by querying by mimeType and name
	folderId = drive.files().list(q = "mimeType = 'application/vnd.google-apps.folder' and name = '" + foldername +"'", pageSize=10, fields="nextPageToken, files(id, name)").execute()
	# this gives us a list of all folders with that name
	#print("folderId", folderId)

	folderIdResult = folderId.get('files', [])
	# however, we know there is only 1 folder with that name, so we just get the id of the 1st item in the list
	id = folderIdResult[0].get('id')


	# Now, using the folder ID gotten above, we get all the files from
	# that particular folder
	results = drive.files().list(q = "'" + id + "' in parents", pageSize=10, fields="nextPageToken, files(id, name)").execute()
	items = results.get('files', [])

	return items

def main():
    #st.write(templates.load_css(), unsafe_allow_html=True)
    st.title('Search Image')
    search = ""
    search = st.text_input('Enter search words:')
    if search:
        #print("search", search)
        folderslist = getFiles('BLOCK PHOTOS')
        #print("folderslist", folderslist)

        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)

        targetfolderlist = dict()

        for folder in folderslist:
            resource = {
                "oauth2": creds.authorize(Http()),
                "id": folder.get('id'),
                "fields": "files("+ folder.get('name')+',' + folder.get('id')+ ')"',
            }

            res = getfilelist.GetFolderTree(resource)
            idlist = res.get('folders')
            namelist = res.get('names')

            for i in merge(idlist, namelist):
                targetfolderlist[i[0]]=i[1]

        #print("targetfolderlist", targetfolderlist)
        fileslist = list()
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)

        imagefiles = list()
        for folder in folderslist:
            resource = {
                "oauth2": creds.authorize(Http()),
                "id": folder.get('id'),
            }
        res = getfilelist.GetFileList(resource)
        filelist = res.get('fileList')

        for item in filelist:
            test = item.get('files')
            for item1 in test:
                if 'image' in item1.get('mimeType'):
                    imagefiles.append(test)
        

        i = 0

        for image in imagefiles:
        	for img in image:
        		parentid = img.get('parents')[0]
        		#print("parentid", parentid)
        		parentname = targetfolderlist.get(parentid)
        		#print("parentname", parentname)
        		#print("search", search)
        		if parentname == search:
        			path = "https://drive.google.com/uc?export=view&id=" + img.get('id')
        			#print("path", path)
        			if path not in showimglist:
                        imgid = imagepath.split("id=")[1]
                        url = "https://drive.google.com/uc?export=download&id=" + imgid
                        res = requests.get(url, stream = True)
                        file_name = os.path.dirname(os.path.abspath(__file__)) + "/test.jpg"
                        if res.status_code == 200:
                            with open(file_name,'wb') as f:
                                shutil.copyfileobj(res.raw, f)
                                print('Image sucessfully Downloaded: ',file_name)
                        else:
                            print('Image Couldn\'t be retrieved')
                            print("file_name", file_name)
                            showimglist.append(file_name)
        				#st.image(path, caption=path)


        # Center the header.
        #col_h = st.columns([1, 3])
        #with col_h[1]:
        #	st.header('Streamlit Photo Viewer')

        with st.container():
        	col_1 = st.columns([1, 1])

        	# Image holder.
        	with col_1[0]:
        		st.image(showimglist[st.session_state.idx], use_column_width=True)
        		st.button('Previous', on_click=view_previous)
        		st.button('Next', on_click=view_next)
        		st.button('WhatsApp', on_click=share_whatsapp)

        	# Json holder
        	#with col_1[1]:
        	#	json_file = f'{showimglist[st.session_state.idx]}.json'
        		# Convert json file to a python dict.
        	#	with open(json_file) as json_file:
        	#		data = json.load(json_file)
        	#	st.json(data, expanded=False)
        				

        				#showimglist.append(path)

        #showImagesnew(showimglist)

        #st.image(showimglist, width = 300)
        			#imagepath = img.get('webViewLink')
        			#print("imagepath", imagepath)
        			#imagevalue = Image.open(imagepath)
        			#st.image(imagevalue)
        			#res = requests.get(imagepath, stream = True)
        			#if res.status_code == 200:
        			#	with open(file_name,'wb') as f:
        			#		shutil.copyfileobj(res.raw, f)
        			#		print('Image sucessfully Downloaded: ',file_name)
        			#else:
        			#	print('Image Couldn\'t be retrieved')

        #for image in imagefiles

        #results = utils.index_search(es, INDEX, search, st.session_state.tags,
        #                             0, PAGE_SIZE)
        #total_hits = results['aggregations']['match_count']['value']
        # show number of results and time taken
        #st.write(templates.number_of_results(total_hits, results['took'] / 1000),
        #         unsafe_allow_html=True)
        # show popular tags
        #popular_tags_html = templates.tag_boxes(search, results['sorted_tags'][:10],
        #                                        st.session_state.tags)
        #st.write(popular_tags_html, unsafe_allow_html=True)
        # search results
        

        #for i in imagefiles:
        #    st.write(i)
            
if __name__ == '__main__':
    main()