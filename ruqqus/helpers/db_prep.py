import psycopg2
from os import environ

conn = psycopg2.connect(environ.get("DATABASE_URL"))
c=conn.cursor()

'''
PostgreSQL server-side functions
For faster sorting and pagination
'''

#Clear any errors (for testing)
#c.execute("ROLLBACK TRANSACTION")

def prep_database():

    #======= SUBMISSIONS =========

    #ups
    c.execute("""
    CREATE OR REPLACE FUNCTION ups(submissions)
    RETURNS bigint AS '
      SELECT COUNT(*)
      FROM votes
      LEFT JOIN users
      ON votes.user_id = users.id
      WHERE users.is_banned=0
        AND votes.vote_type=1
        AND votes.submission_id=$1.id
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    #downs
    c.execute("""
    CREATE OR REPLACE FUNCTION downs(submissions)
    RETURNS bigint AS '
      SELECT COUNT(*)
      FROM votes
      LEFT JOIN users
      ON votes.user_id = users.id
      WHERE users.is_banned=0
        AND votes.vote_type=-1
        AND votes.submission_id=$1.id
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    #age
    c.execute("""
    CREATE OR REPLACE FUNCTION age(submissions)
    RETURNS int AS '
      SELECT CAST( EXTRACT( EPOCH FROM CURRENT_TIMESTAMP) AS int) - $1.created_utc
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    #score
    c.execute("""
    CREATE OR REPLACE FUNCTION score(submissions)
    RETURNS bigint AS '
      SELECT ($1.ups - $1.downs)
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    #rank hot
    c.execute("""
    CREATE OR REPLACE FUNCTION rank_hot(submissions)
    RETURNS float AS '
      SELECT CAST(($1.ups - $1.downs) AS float)/((CAST(($1.age+5000) AS FLOAT)/100.0)^(0.7))
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    #rank controversial
    c.execute("""
    CREATE OR REPLACE FUNCTION rank_fiery(submissions)
    RETURNS float AS '
      SELECT SQRT(CAST(($1.ups * $1.downs) AS float))/((CAST(($1.age+5000) AS FLOAT)/100.0)^(0.7))
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    #comment count
    c.execute("""
    CREATE OR REPLACE FUNCTION comment_count(submissions)
    RETURNS bigint AS '
      SELECT COUNT(*)
      FROM comments
      WHERE is_banned=false
        AND is_deleted=false
        AND parent_submission = $1.id
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    #activity sort
    c.execute("""
    CREATE OR REPLACE FUNCTION rank_activity(submissions)
    RETURNS float AS '
      SELECT CAST($1.comment_count AS float)/((CAST(($1.age+5000) AS FLOAT)/100.0)^(0.7))
    '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)
    
    #flag count
    c.execute("""
    CREATE OR REPLACE FUNCTION flag_count(submissions)
    RETURNS bigint AS '
      SELECT COUNT(*)
      FROM flags
      JOIN users ON flags.user_id=users.id
      WHERE post_id=$1.id
      AND users.is_banned=0
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)
    

    #=========COMMENTS========

    #ups
    c.execute("""
    CREATE OR REPLACE FUNCTION ups(comments)
    RETURNS bigint AS '
      SELECT COUNT(*)
      FROM commentvotes
      LEFT JOIN users
      ON commentvotes.user_id = users.id
      WHERE users.is_banned=0
        AND commentvotes.vote_type=1
        AND commentvotes.comment_id=$1.id
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    #downs
    c.execute("""
    CREATE OR REPLACE FUNCTION downs(comments)
    RETURNS bigint AS '
      SELECT COUNT(*)
      FROM commentvotes
      LEFT JOIN users
      ON commentvotes.user_id = users.id
      WHERE users.is_banned=0
        AND commentvotes.vote_type=-1
        AND commentvotes.comment_id=$1.id
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    #age
    c.execute("""
    CREATE OR REPLACE FUNCTION age(comments)
    RETURNS int AS '
      SELECT CAST( EXTRACT( EPOCH FROM CURRENT_TIMESTAMP) AS int) - $1.created_utc
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    #flag count
    c.execute("""
    CREATE OR REPLACE FUNCTION flag_count(comments)
    RETURNS bigint AS '
      SELECT COUNT(*)
      FROM commentflags
      JOIN users ON commentflags.user_id=users.id
      WHERE comment_id=$1.id
      AND users.is_banned=0
      '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)
    

    #===========USERS=============

    c.execute("""
    CREATE OR REPLACE FUNCTION energy(users)
    RETURNS numeric AS '
     SELECT COALESCE(
     (
      SELECT SUM(submissions.score)
      FROM submissions
      WHERE submissions.author_id=$1.id
        AND submissions.is_banned=false
        AND submissions.is_deleted=false
      ),
      0
      )
    '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT
    """)

    c.execute("""
    CREATE OR REPLACE FUNCTION referral_count(users)
    RETURNS bigint AS'
        SELECT COUNT(*)
        FROM USERS
        WHERE users.is_banned=0
        AND users.referred_by=$1.id
    '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)

    ##c.execute("""
    ##CREATE OR REPLACE FUNCTION overview(users)
    ##RETURNS refcursor AS '
    ##  SELECT * from
    ##  (
    ##    select id, created_utc, 'submission' as item_type,
    ##    from submissions
    ##    where author_id=$1.id
    ##    union all
    ##    select id, created_utc, 'comment' as item_type,
    ##    from comments
    ##    where author_id=$1.id
    ##  ) as t1
    ##order by created_utc desc
    ##offset 0
    ##limit 5
    ##'
    ##LANGUAGE SQL
    ##IMMUTABLE
    ##RETURNS NULL ON NULL INPUT
    ##""")

    #==========RANDOM IMAGE SPLASH SELECTION=========

    c.execute("""
    CREATE OR REPLACE FUNCTION splash(text)
    RETURNS setof images AS '
      SELECT *
      FROM images
      WHERE state=$1
      ORDER BY random()
      LIMIT 1
    '
    LANGUAGE SQL
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
    """)
    conn.commit()
    c.close()
    conn.close()

prep_database()
