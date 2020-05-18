-- 创建表格
USE taobao_data;
DROP TABLE USER;
CREATE TABLE USER (
	user_id INT NOT NULL,
	item_id INT NOT NULL,
	category_id INT NOT NULL,
	behavetype VARCHAR(10) NOT NULL,
	dates VARCHAR(10) NOT NULL,
	times VARCHAR(10) NOT NULL);
SELECT dates FROM USER LIMIT 0,100;
DESC USER;
-- 导入数据
LOAD DATA LOCAL INFILE 'E:\实习\userbehavior\UserBehavioDone.csv'
INTO TABLE USER 
FIELDS TERMINATED BY ','
IGNORE 1 LINES;

-- 提取小时数据
ALTER TABLE USER ADD hours CHAR(10) NULL;

UPDATE USER
SET hours =LEFT(times,2);     #截取小时的数据

-- （一）、总体运营分析
CREATE VIEW userbehave AS
SELECT user_id,COUNT(behavetype) num,SUM(IF(behavetype='pv',1,0)) pv,SUM(IF(behavetype='cart',1,0)) cartbox,SUM(IF(behavetype='fav',1,0)) favor,SUM(IF(behavetype='buy',1,0)) buy,dates
FROM USER
GROUP BY user_id,dates,hours
ORDER BY user_id,dates,hours
-- 1.计算浏览量：pv
SELECT behavetype,COUNT(*)
FROM USER
WHERE behavetype='pv';
-- 2.查看各类别的访客数
SELECT behavetype,COUNT(DISTINCT user_id)
FROM USER
GROUP BY behavetype
ORDER BY COUNT(DISTINCT user_id) DESC;

-- 3.计算日均访客数
SELECT dates,COUNT(DISTINCT user_id)
FROM USER
WHERE behavetype='pv'
GROUP BY dates
ORDER BY dates;
-- 4.计算独立访客数uv
SELECT COUNT(DISTINCT user_id)
FROM USER;
-- 5.计算有购买行为的访客数
SELECT COUNT(DISTINCT user_id)AS 购买用户量
FROM USER
WHERE behavetype='buy';
-- 6.人均页面访客数
SELECT ((SELECT COUNT(*) FROM USER WHERE behavetype='pv')/COUNT(DISTINCT user_id))AS 'pv/uv'
FROM USER;
-- 7.转化率=（产生购买行为的客户人数 / 所有到达店铺的访客人数）× 100%。
SELECT t1.dates,t1.bv AS 购买用户数,t2.uv AS 访客数 ,CONCAT(ROUND(t1.bv/t2.uv*100,2),'%') conversion
FROM(SELECT dates,COUNT(DISTINCT user_id) bv FROM USER WHERE behavetype='buy' GROUP BY dates)AS t1
LEFT JOIN 
(SELECT dates,COUNT(DISTINCT user_id) uv FROM USER  GROUP BY dates)AS t2
ON t1.dates=t2.dates
ORDER BY dates;

-- 二、漏斗分析
-- 1.计算跳失率
SELECT ((SELECT COUNT(DISTINCT user_id)
FROM USER
WHERE user_id NOT IN(SELECT user_id FROM USER WHERE behavetype='buy')
AND user_id NOT IN(SELECT user_id FROM USER WHERE behavetype='cart')
AND user_id NOT IN(SELECT user_id FROM USER WHERE behavetype='fav'))/(SELECT COUNT(DISTINCT user_id) FROM USER ))AS BR;

-- 2.漏斗图
-- 转化漏斗
SELECT behavetype,COUNT(user_id)
FROM USER
GROUP BY behavetype
ORDER BY COUNT(user_id) DESC;
-- 独立访客转化
SELECT behavetype,COUNT(DISTINCT user_id)
FROM USER
GROUP BY behavetype
ORDER BY COUNT(DISTINCT user_id) DESC;

-- 三、一天不同时间段的用户分析
-- 1.不同时间段的点击量
SELECT t1.hours,t1.浏览量,t1.加购量,t1.收藏量,t1.购买量,t2.用户数,t3.购买用户数
FROM(SELECT hours,SUM(CASE WHEN behavetype='pv' THEN 1 ELSE 0 END) AS 浏览量,
SUM(CASE WHEN behavetype='cart' THEN 1 ELSE 0 END)AS 加购量,
SUM(CASE WHEN behavetype='fav' THEN 1 ELSE 0 END)AS 收藏量,
SUM(CASE WHEN behavetype='buy' THEN 1 ELSE 0 END)AS 购买量
FROM USER
GROUP BY hours)AS t1
LEFT JOIN
(SELECT hours,COUNT(DISTINCT user_id)AS 用户数
FROM USER
GROUP BY hours)AS t2
ON t1.hours=t2.hours
LEFT JOIN(SELECT hours,COUNT(DISTINCT user_id)AS 购买用户数
FROM USER
WHERE behavetype='buy'
GROUP BY hours)AS t3
ON t1.hours=t3.hours
ORDER BY t1.hours;


-- 四、用户行为分析
-- 1.各用户的行为
SELECT user_id,COUNT(behavetype),
SUM(CASE WHEN behavetype='pv' THEN 1 ELSE 0 END) AS 浏览率,
SUM(CASE WHEN behavetype='cart' THEN 1 ELSE 0 END)AS 加购量,
SUM(CASE WHEN behavetype='fav' THEN 1 ELSE 0 END)AS 收藏量,
SUM(CASE WHEN behavetype='buy' THEN 1 ELSE 0 END)AS 购买量
FROM USER
GROUP BY user_id
ORDER BY COUNT(behavetype) DESC;

-- 2.变现——复购分析
SELECT t1.购买次数,COUNT(t1.user_id)用户数
FROM(SELECT user_id,COUNT(*)AS 购买次数 FROM USER WHERE behavetype='buy'
GROUP BY user_id
ORDER BY COUNT(*) DESC)AS t1
GROUP BY t1.购买次数 
ORDER BY t1.购买次数;
-- 3.复购率：产生两次或两次以上购买的用户占购买用户的比例:66.28%

SELECT ((SELECT COUNT(DISTINCT user_id) FROM USER
WHERE user_id IN (SELECT user_id FROM USER WHERE behavetype='buy' GROUP BY user_id HAVING COUNT(user_id)>=2))
/(SELECT COUNT(DISTINCT user_id)AS 用户数 FROM USER WHERE behavetype='buy'))AS 复购率;

-- (五)RMF分析
SELECT allrank.user_id,allrank.recent,allrank.buynum,
CONCAT(CASE WHEN allrank.r_r <= (6382)/4 THEN '4'
       WHEN allrank.r_r > (6382)/4 AND allrank.r_r <=(6382)/2 THEN '3'
       WHEN allrank.r_r > (6382)/2 AND allrank.r_r <=(6382)/4*3 THEN '2'
       ELSE '1' END,
       CASE WHEN allrank.f_r<=(856)/4 THEN '4' 
       WHEN allrank.f_r > (856)/4 AND allrank.f_r <=(856)/2 THEN '3'
       WHEN allrank.f_r > (856)/2 AND allrank.f_r <=(856)/4*3 THEN '2'
       ELSE '1' END)AS user_value
FROM(SELECT rencent_value.user_id,rencent_value.recent,rank()over(ORDER BY rencent_value.recent) r_r,frequency_value.buynum,rank()over(ORDER BY frequency_value.buynum DESC) f_r
FROM 
(SELECT user_id,DATEDIFF('2017-12-04',MAX(dates))AS recent
FROM USER
WHERE behavetype='buy'
GROUP BY user_id)AS rencent_value
LEFT JOIN(SELECT user_id,COUNT(*)AS buynum
FROM USER
WHERE behavetype='buy'
GROUP BY user_id)AS frequency_value
ON rencent_value.user_id=frequency_value.user_id)AS allrank
ORDER BY user_value DESC;

SELECT allrank.user_id,allrank.recent,allrank.buynum,
CONCAT(CASE WHEN allrank.r_r<=(6382)/4 THEN '4' 
      WHEN allrank.r_r>(6382)/4 AND allrank.r_r<=(6382)/2 THEN '3'
            WHEN allrank.r_r>(6382)/2 AND allrank.r_r<=(6382)/4*3 THEN '2'
   ELSE '1' END,
       CASE WHEN allrank.f_r<=(856)/4  THEN '4' 
   WHEN allrank.f_r>(856)/4  AND allrank.f_r<=(856)/2 THEN '3'
            WHEN allrank.f_r>(856)/2 AND allrank.f_r<=(856)/4*3 THEN '2'
            ELSE '1' END
      )AS user_value
FROM(
SELECT recent_value.user_id,recent_value.recent,rank()over(ORDER BY recent_value.recent) r_r, frequency_value.buynum,rank()over(ORDER BY frequency_value.buynum DESC) f_r
FROM
(SELECT user_id,DATEDIFF('2017-12-04',MAX(dates))  recent
FROM USER
WHERE behavetype='buy'
GROUP BY user_id) AS recent_value 
JOIN
(SELECT user_id,COUNT(user_id) buynum
FROM USER
WHERE behavetype='buy'
GROUP BY user_id) AS frequency_value
ON recent_value.user_id = frequency_value.user_id
) AS allrank
ORDER BY user_value;


-- （六）商品销售分析
-- 1.商品销量分布
SELECT t1.销量,COUNT(*)AS 商品数
FROM(SELECT item_id,COUNT(*)AS 销量
FROM USER
WHERE behavetype='buy'
GROUP BY item_id
ORDER BY 销量)t1
GROUP BY t1.销量
ORDER BY t1.销量;
-- 2.畅销品及其品类分析
-- （1）销量
SELECT category_id,item_id,COUNT(*)AS 销量
FROM USER
WHERE behavetype='buy'
GROUP BY item_id
ORDER BY 销量 DESC
LIMIT 20;

-- （2）浏览量
SELECT category_id,item_id,COUNT(*)AS 浏览量
FROM USER
WHERE behavetype='pv'
GROUP BY item_id
ORDER BY 浏览量 DESC
LIMIT 20;

-- （3）加购量
SELECT category_id,item_id,COUNT(*)AS 加购量
FROM USER
WHERE behavetype='cart'
GROUP BY item_id
ORDER BY 加购量 DESC
LIMIT 20;

-- （4）收藏
SELECT category_id,item_id,COUNT(*)AS 收藏量
FROM USER
WHERE behavetype='fav'
GROUP BY item_id
ORDER BY 收藏量 DESC
LIMIT 20;

-- （七）（3）商品购买转化率
SELECT t1.category_id,t1.item_id,t1.销量,t2.浏览量,CONCAT(ROUND(t1.销量/t2.浏览量*100,2),'%') conversion
FROM
(SELECT category_id,item_id,COUNT(*)AS 销量
FROM USER
WHERE behavetype='buy'
GROUP BY item_id)AS t1
LEFT JOIN
(SELECT category_id,item_id,COUNT(*)AS 浏览量
FROM USER
WHERE behavetype='pv'
GROUP BY item_id)AS t2
ON t1.item_id=t2.item_id
ORDER BY conversion DESC
LIMIT 200;