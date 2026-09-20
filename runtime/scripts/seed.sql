INSERT INTO "Academy"(id,name,slug) VALUES
('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','Rally Table Tennis Academy','rally'),
('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb','Spin Studio','spin-studio');
INSERT INTO "Branch"(id,"academyId",name,city,address) VALUES
('a1111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','Indiranagar','Bengaluru','12, 100 Feet Road, Indiranagar'),
('a2222222-2222-4222-8222-222222222222','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','Whitefield','Bengaluru','8, ECC Road, Whitefield'),
('b1111111-1111-4111-8111-111111111111','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb','Main studio','Pune','24, Baner Road');
INSERT INTO "TableResource"(id,"academyId","branchId",name)
SELECT gen_random_uuid(),"academyId",id,'Table ' || n FROM "Branch" CROSS JOIN generate_series(1,3) n;
INSERT INTO "Membership"(id,"academyId","userId",email,name,roles,"allBranches") VALUES
('c1111111-1111-4111-8111-111111111111','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','11111111-1111-4111-8111-111111111111','admin@rally.example','Aarav Mehta',ARRAY['ADMIN']::"Role"[],true),
('c2222222-2222-4222-8222-222222222222','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','22222222-2222-4222-8222-222222222222','coach@rally.example','Nisha Rao',ARRAY['COACH']::"Role"[],false),
('c3333333-3333-4333-8333-333333333333','bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb','33333333-3333-4333-8333-333333333333','admin@spin.example','Dev Sharma',ARRAY['ADMIN']::"Role"[],true);
INSERT INTO "MemberBranch"("academyId","membershipId","branchId") VALUES
('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','c2222222-2222-4222-8222-222222222222','a1111111-1111-4111-8111-111111111111');
INSERT INTO "PlatformOwner"("userId") VALUES ('44444444-4444-4444-8444-444444444444');
INSERT INTO "Audit"(id,"academyId","actorId",action,detail) VALUES
(gen_random_uuid(),'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','11111111-1111-4111-8111-111111111111','academy.initialized','Local preview academy created'),
(gen_random_uuid(),'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb','33333333-3333-4333-8333-333333333333','academy.initialized','Local preview academy created');
