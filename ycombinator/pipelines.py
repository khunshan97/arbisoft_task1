from itemadapter import ItemAdapter
import sqlite3


class SqlitePipeline:

    def __init__(self):
        self.con = sqlite3.connect('demo.db')
        self.cur = self.con.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs(
            job_id TEXT,
            title TEXT,
            location TEXT,
            company TEXT
        )
        """)

    def process_item(self, item, spider):
        self.cur.execute("select * from jobs where job_id = ?", (item['job_id'],))
        result = self.cur.fetchone()
        if result:
            spider.logger.warn("Item already in database: %s" % item['title'])
        else:
            self.cur.execute("""
                       INSERT INTO jobs (job_id, title, location, company) VALUES (?, ?, ?,?)
                   """,
                             (
                                 item['job_id'],
                                 str(item['title']),
                                 item['location'],
                                 item['company']
                             ))
            self.con.commit()
        return item
