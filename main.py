'''
    Autor proiect: Ursache Ana-Maria

    Descriere proiect:
        In cadrul acestui proiect se va dori afisarea, pe o pagina web, a unor informatii de pe un subreddit.
        Informatiile necesare sunt: numele subreddit-ului, descrierea sa, numarul de subscriberi,
        numarul de active users, thread-uri highlightate, numarul de postari din ultimele 24h si o statistica
        referitoare la cele mai folosite label-uri in ultimele X thread-uri hot.
'''
import matplotlib
matplotlib.use('Agg')
# backend ne-interactive pentru a putea vedea si png-ul, dar si documentul styles.css

from datetime import datetime
from flask import Flask, render_template
import matplotlib.pyplot as plt
import praw
import os
import time

'''    
    Intr-o prima instanta, trebuie sa ne conectam la reddit, iar pentru asta
    trebuie mai intai sa creez o aplicatie pe reddit(de tip script): https://www.reddit.com/prefs/apps/,
    aici cu numele de "Report-project". Tot de pe acest site, dupa ce am facut aplicatia, se va afla si codul "secret"
    si id-ul de client care e primit pe email.

    Vom folosi libraria praw, care face usoara conectarea si extragerea de informatii de pe reddit.
'''

SUBREDDIT_NAME = "Romania"

REDDIT_SECRET = "OECmlM0WgL6y-2zwuYdeWTzWiVPvxw"
REDDIT_CLIENT_ID = "_NFceCl9zhFpx_in9zYMUg"
REDDIT_USERNAME = "Ana_2662"
REDDIT_PASSWORD = "ana040930.Ana"

LIMIT_POSTS = 1500


def connecting_to_reddit():
    '''
        Prin intermediul librariei praw, cu datele avute, ne conectam la reddit cu metoda praw.Reddit().
    '''

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_SECRET,
        user_agent="project",
        password=REDDIT_PASSWORD,
        username=REDDIT_USERNAME,
    )
    return reddit


def testing_the_connection():
    reddit = connecting_to_reddit()
    print("\nTestare conectare la reddit:")
    for submission in reddit.subreddit(SUBREDDIT_NAME).hot(limit=4):
        print(submission.title)
    print("-" * 20)


def extracting_simple_details():
    '''
        Pentru a putea obtine datele de care avem nevoie(in legatura cu acest subreddit), trebuie sa utilizam
        functia .subreddit("Romania") pentru a putea toate informatiile necesare.

        Titlul este completat cu "r/" pentru a evidentia faptul ca este un subreddit, age restriction este completat cu "NSFW"
        daca subreddit-ul are restrictie de varsta sau "Open for everyone" daca nu are, iar numarul de subscriberi este afisat
        in functie de numarul acestora, astfel incat sa fie mai usor de citit si afisat pe pagina web.
    '''

    reddit = connecting_to_reddit()
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    subreddit_name = subreddit.display_name
    title = "r/" + subreddit_name

    subreddit_title = subreddit.title
    subredddit_description = subreddit.public_description
    subredddit_subscribers_nr = subreddit.subscribers
    subreddit_active_users = subreddit.active_user_count

    subreddit_age = subreddit.over18
    age = "NSFW" if subreddit_age else "Open for everyone"

    if subredddit_subscribers_nr >= 1_000_000:
        display_subscribers = f"{subredddit_subscribers_nr / 1_000_000:.1f}M"
    elif subredddit_subscribers_nr >= 1_000:
        display_subscribers = f"{subredddit_subscribers_nr / 1_000:.1f}k"
    else:
        display_subscribers = subredddit_subscribers_nr

    print("\nTestare obtinere detalii subreddit:")
    print(subreddit_name, subreddit_title, subreddit_age, subredddit_description, display_subscribers,
          subreddit_active_users)
    print("-" * 20)

    return title, subreddit_title, subredddit_description, display_subscribers, subreddit_active_users, age


def extracting_nr_posts_in_24h():
    '''
        Pentru a evidentia numarul acelor postari din ultimele 24 de ore, sunt mai multe metode care se pot folosi, dar ma
        voi ajuta de libraria time pentru a extrage timpul curent al laptopului meu. Voi compara acest timp cu
        momentul crearii fiecarei postari gasite si voi lua in considerare la suma calculata doar acele postari
        care au fost facute in ultimele 24 de ore.
    '''

    reddit = connecting_to_reddit()
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    current_time = time.time()
    nr_posts_in_24h = sum(
        1 for post in subreddit.new(limit=None) if current_time - post.created_utc <= 86400
    )

    print("\nTestare numar de postari in 24h:")
    print(f"{nr_posts_in_24h} de postari")
    print("-" * 20)

    return nr_posts_in_24h


def extracting_sticky_posts():
    '''
        O alta componenta importanta a acestui proiect este detalierea postarilor de tip "sticky",
        adica a acelor postari ce au fost pinuite de catre moderatorii subreddit-ului.

        Pentru a le obtine, trebuie sa luam in calcul faptul ca, pe Reddit, este setat un numar maxim
        de 2 postari de acest tip care pot exista la un subreddit. De aceea, voi
        prelua ambele postari sticky, iar pentru ca nu stiu daca nu exista ambele/nici macar una, ma voi
        folosi de un bloc try-except pentru a evita aparitia unor erori.

        Pentru fiecare postare, se vor afisa pe pagina web metadalele acestora, cum ar fi titlul, autorul, upvotes-urile,
        cand a fost creata(formatata cu libraria "datetime"), cate comentarii are si textul acesteia. De asemenea, 
        va aparea si un link catre acea postare scris, dar si sub forma de buton.
    '''

    reddit = connecting_to_reddit()
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    sticky_posts = []

    try:
        first_pinned_post = subreddit.sticky(number=1)
    except Exception as e:
        print(f"Au aparut probleme in momentul in care s-au luat postarile sticky.")
    else:
        sticky_posts.append(first_pinned_post)

    try:
        second_pinned_post = subreddit.sticky(number=2)
    except Exception as e:
        print(f"Au aparut probleme in momentul in care s-au luat postarile sticky.")
    else:
        sticky_posts.append(second_pinned_post)

    if len(sticky_posts) == 2:
        sticky_post1 = [
            sticky_posts[0].title,
            sticky_posts[0].author,
            sticky_posts[0].score,
            datetime.fromtimestamp(sticky_posts[0].created_utc).strftime(
                '%Y-%m-%d %H:%M:%S'),
            sticky_posts[0].num_comments,
            sticky_posts[0].selftext,
            sticky_posts[0].url
        ]

        sticky_post2 = [
            sticky_posts[1].title,
            sticky_posts[1].author,
            sticky_posts[1].score,
            datetime.fromtimestamp(sticky_posts[1].created_utc).strftime(
                '%Y-%m-%d %H:%M:%S'),
            sticky_posts[1].num_comments,
            sticky_posts[1].selftext,
            sticky_posts[1].url
        ]

    elif len(sticky_posts) == 1:
        sticky_post1 = [
            sticky_posts[0].title,
            sticky_posts[0].author,
            sticky_posts[0].score,
            datetime.fromtimestamp(sticky_posts[0].created_utc).strftime(
                '%Y-%m-%d %H:%M:%S'),
            sticky_posts[0].num_comments,
            sticky_posts[0].selftext,
            sticky_posts[0].url
        ]

        sticky_post2 = [None, None, None, None, None, None, None]

    else:
        sticky_post1 = [None, None, None, None, None, None, None]
        sticky_post2 = [None, None, None, None, None, None, None]

    return sticky_post1, sticky_post2, sticky_posts


def extracting_flairs():
    '''
        In continuare, pentru a putea face o statistica cu cele mai folosite label-uri(flairs, maxim 1 pe thead) in ultimele X thread-uri hot,
        voi trece prin toate aceste thread-uri si voi aduna label-urile gasite intr-un dictionar(most_used_flairs) pe care 
        mai apoi il voi sorta dupa frecventa sa, descrescator.
    '''

    reddit = connecting_to_reddit()
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    flairs = {}

    for post in subreddit.hot(limit=LIMIT_POSTS):
        if post.link_flair_text is None:
            continue
        else:
            if post.link_flair_text in flairs:
                flairs[post.link_flair_text] += 1
            else:
                flairs[post.link_flair_text] = 1

    most_used_flairs = dict(
        sorted(flairs.items(), key=lambda item: item[1], reverse=True))

    print("\nTestare statistica label-uri:")
    print(most_used_flairs)
    print("-" * 20)

    making_the_statistics(most_used_flairs)

    return most_used_flairs


def making_the_statistics(most_used_flairs):
    '''
        In aceasta functie se va crea un grafic pentru statisticile dorite(pentru flairs) si se va salva ca poza pentru
        a putea fi afisat pe pagina web.
    '''

    labels = list(most_used_flairs.keys())
    values = list(most_used_flairs.values())

    plt.figure(figsize=(10, 8))
    plt.bar(labels, values)
    plt.xlabel('Flairs')
    plt.ylabel('Frequency')
    plt.title('Most Used Flairs in Hot Posts')

    plt.xticks(rotation=30, ha='right', fontsize=8)
    img_path = os.path.join('static', 'flairs_graph.png')
    plt.savefig(img_path)

    plt.close()

    return labels, values


'''
    In final, este necesar crearea unui pagini web in care sa afisam toate datele colectata in cadrul proiectului.
    
    Intial voi face o un document de tip html in care voi completa caracteristicile la modul general, iar ulterior
    ma voi ajuta de framework-ul Flask pentru a putea trece datele in pagina web.
    
    Cu functia render_template incarc practic acest template si ii trimit toate datele necesare.

'''

testing_the_connection()
title, subreddit_title, subredddit_description, display_subscribers, subreddit_active_users, age = extracting_simple_details()
nr_posts_in_24h = extracting_nr_posts_in_24h()
sticky_post1, sticky_post2, sticky_posts = extracting_sticky_posts()
most_used_flairs = extracting_flairs()
labels, values = making_the_statistics(most_used_flairs)

app = Flask(__name__)
@app.route('/')
def show_report():

    return render_template('report.html',
                           title=title, subreddit_title=subreddit_title,
                           subredddit_description=subredddit_description,
                           subredddit_subscribers_nr=display_subscribers,
                           subreddit_active_users=subreddit_active_users,
                           nr_posts_in_24h=nr_posts_in_24h, age=age,

                           sticky_posts=sticky_posts,

                           thread_title=sticky_post1[0],
                           thread_author=sticky_post1[1],
                           thread_upvotes=sticky_post1[2],
                           thread_date=sticky_post1[3],
                           thread_comments_nr=sticky_post1[4],
                           thread_text=sticky_post1[5],
                           thread_url=sticky_post1[6],

                           threads_title=sticky_post2[0],
                           threads_author=sticky_post2[1],
                           threads_upvotes=sticky_post2[2],
                           threads_date=sticky_post2[3],
                           threads_comments_nr=sticky_post2[4],
                           threads_text=sticky_post2[5],
                           threads_url=sticky_post2[6],

                           labels=labels, values=values,
                           )


if __name__ == '__main__':
    app.run(debug=True)
