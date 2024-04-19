/*
 Завдання на SQL до лекції 03.
 */

/*
1.
Вивести кількість фільмів в кожній категорії.
Результат відсортувати за спаданням.
*/

select
    ca.name, count(distinct c.film_id) films_cnt
from
    public.film_category c
left join
    category ca on c.category_id = ca.category_id
group by
    c.category_id, ca.name
order by
    films_cnt desc;

/*
2.
Вивести 10 акторів, чиї фільми брали на прокат найбільше.
Результат відсортувати за спаданням.
*/


with
films_rents as (
    -- cte-таблиця кількісті прокатів для кожного фільму
    select
        i.film_id,
        count(distinct r.rental_id) count_rents
    from
        rental r
    left join
        inventory i
        on r.inventory_id = i.inventory_id
    group by
        i.film_id
    order by
        count_rents desc),
actor_films_rents as (
    --cte-таблиця кількісті прокатів для кожного фільму з прив'язкою акторів
    select
        fa.actor_id,
        fa.film_id,
        fr.count_rents
    from
        film_actor fa
    left join
        films_rents fr
        on fa.film_id = fr.film_id)
-- розрахунок суми кількості прокатів усіх фільмів для кожного актора
select
    concat(a.first_name || ' ' || a.last_name) actor_name,
    sum(afr.count_rents) count_rents_actor
from
    actor_films_rents afr
left join
    actor a
    on afr.actor_id = a.actor_id
group by concat(a.first_name || ' ' || a.last_name)
order by count_rents_actor desc
limit 10
;


/*
3.
Вивести категорія фільмів, на яку було витрачено найбільше грошей
в прокаті
*/

with
films_rents as ( -- cte-таблиця кількісті прокатів для кожного фільму
    select
        r.rental_id,
        i.film_id,
        c."name" as category_name
    from
        rental r
    left join
        inventory i
        on r.inventory_id = i.inventory_id
    left join
        film_category fc
        on i.film_id = fc.film_id
    left join
        category c
        on fc.category_id = c.category_id
    )
select
    category_name,
    sum(amount) sales
from
    (select
        p.*,
        fr.rental_id,
        fr.film_id,
        fr.category_name
        from
            payment p
        left join
            films_rents fr
            on p.rental_id = fr.rental_id) as t
group by
    category_name
order by
    sales desc
limit 1;

/*
!!! В таблиці payment є незрозумілі дані (неунікальні rental_id).
Для одного rental_id (а саме rental_id = 4591) є шість payment_id
Всі інші id мають відношення один до одного.
Тому к-сть payment_id на 5 більша за к-сть rental_id.

select * from payment where rental_id = 4591;
*/

/*
4.
Вивести назви фільмів, яких не має в inventory.
Запит має бути без оператора IN
*/

select
    f.title
from
    film f
left join
    inventory i
    on f.film_id = i.film_id
where i.film_id is null;


/*
5.
Вивести топ 3 актори, які найбільше зʼявлялись в категорії фільмів “Children”.
*/
select
    concat(a.first_name || ' ' || a.last_name) actor_name,
    count(distinct fa.film_id) films_cnt_children
from
    film_actor fa
left join
    actor a
    on fa.actor_id = a.actor_id
where film_id in (
    select
        fc.film_id
    from
        film_category fc
    left join
        category c
        on fc.category_id = c.category_id
    where c."name" = 'Children')
group by
    concat(a.first_name || ' ' || a.last_name)
order by
    films_cnt_children desc
limit 3;
