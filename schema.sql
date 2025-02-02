create table
  public.barrel_table (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    sku text null,
    quantity bigint null,
    r integer null,
    g integer null,
    b integer null,
    d integer null,
    name text null,
    constraint barrel_table_pkey primary key (id)
  ) tablespace pg_default;

create table
  public.bottle_table (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    sku text null,
    name text null,
    quantity integer null,
    price bigint null,
    r integer null,
    g integer null,
    b integer null,
    d integer null,
    constraint bottle_table_pkey primary key (id)
  ) tablespace pg_default;

create table
  public.cart_items (
    cart_id bigint not null,
    created_at timestamp with time zone not null default now(),
    item_sku text null,
    quantity integer null default 0,
    id bigint generated by default as identity,
    constraint cart_items_pkey primary key (id),
    constraint cart_items_cart_id_fkey foreign key (cart_id) references cart_table (id) on delete cascade
  ) tablespace pg_default;

  create table
  public.cart_table (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    constraint cart_table_pkey primary key (id)
  ) tablespace pg_default;

  create table
  public.cash_ledger (
    id bigint generated by default as identity,
    created_at timestamp with time zone not null default now(),
    type text null,
    description text null,
    amount bigint null,
    balance bigint null,
    constraint cash_ledger_pkey primary key (id)
  ) tablespace pg_default;
