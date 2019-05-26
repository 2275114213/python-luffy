from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.shortcuts import HttpResponse

# from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response

from api.models import (Course, PricePolicy)
from api.utils.auth import  ExpiringTokenAuthentication
from api.utils.response import BaseResponse
from api.utils.exceptions import CommonException

import json
import redis
r = redis.Redis(decode_responses=True)




class ShoppingCar(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    def get(self,request):
        # r.delete(*r.keys())
        """"
        {
    "error_no": 0,
    "data": {
        "total": 1,
        "shopping_car_list": [
            {
                "id": 2,
                "default_price_period": 60,
                "title": "python开发21天",
                "img": "//hcdn1.luffycity.com/static/frontend/course/5/21天_1544059695.5584881.jpeg",
                "relate_price_policy": [
                    {
                        "pk": "4",
                        "relate_price_policy": 30,
                        "valid_period_text": "1个月",
                        "price": 100,
                        "default": false
                    },
                    {
                        "pk": "5",
                        "valid_period": 60,
                        "valid_period_text": "2个月",
                        "price": 200,
                        "default": true
                    },

                ],
                "choose_price_policy_id": 5,
                "default_price": 200,
                "valid_period": 60,
                "valid_period_text": "2个月"
            }
        ]
    }
}

        """
        """
        {
	"error_no": 0,
	"data": {
		"total": 2,
		"myShopCart": [{
			"courseName": "算法入门",
			"courseId": "10",
			"courseImg": "//hcdn1.luffycity.com/static/frontend/course/10/算法_1544008664.5285745.jpeg",
			"coursePrice": "399.0",
			"validPeriod": "6个月",
			"validPeriodId": "180",
			"validPeriodChoices": [{
				"validPeriodId": 10000,
				"validPeriod": "永久有效",
				"price": "99.0",
				"default": false
			}, {
				"validPeriodId": 60,
				"validPeriod": "2个月",
				"price": "199.0",
				"default": false
			}, {
				"validPeriodId": 90,
				"validPeriod": "3个月",
				"price": "299.0",
				"default": false
			}, {
				"validPeriodId": 180,
				"validPeriod": "6个月",
				"price": "399.0",
				"default": true
			}]
		}, {
			"courseName": "Python开发21天入门",
			"courseId": "5",
			"courseImg": "//hcdn1.luffycity.com/static/frontend/course/5/21_1544059739.2676835.jpeg",
			"coursePrice": "9.0",
			"validPeriod": "永久有效",
			"validPeriodId": "10000",
			"validPeriodChoices": [{
				"validPeriodId": 30,
				"validPeriod": "1个月",
				"price": "0.0",
				"default": false
			}, {
				"validPeriodId": 90,
				"validPeriod": "3个月",
				"price": "69.0",
				"default": false
			}, {
				"validPeriodId": 10000,
				"validPeriod": "永久有效",
				"price": "9.0",
				"default": true
			}]
		}],
		"invalidCart": []
	}
}
        :param request:
        :return:
        """
        # r.delete(*r.keys())
        print(r.keys())
        # get 没有request.data 记住 如果获取请求数据
        # r.keys()
        # print(r.keys())
        user_id = request.user.pk
        print(user_id)
        shopping_car_key = settings.SHOPPING_CAR_KEY%(user_id,"*")
        lis = r.keys(shopping_car_key)
        res = {"error_no":0,"data":{}}
        data = {}
        total  = len(lis)
        data["total"] = total

        data["shopping_car_list"] = []
        # data["shopping_car_list1"] = {}
        for item in lis:
            print("relate_price_policy",item)
            ret = json.loads(r.get(item))
            ret1 = json.loads(r.get(item))
            print(ret,"====")
            relate_price_policy1=[]
            print("yuan",ret)
            for key,relate_price_policy_obj in ret["relate_price_policy"].items():
                print(key,relate_price_policy_obj)
                relate_price_policy_obj["pk"]=key
                relate_price_policy1.append(relate_price_policy_obj)
            data["shopping_car_list"].append(ret)
            ret["relate_price_policy"] = relate_price_policy1
            # for key,rerelate_price_policy_obj in ret1["relate_price_policy"].items():
            #     rerelate_price_policy_obj["pk"] = key
                # data["shopping_car_list1"]["relate_price_policy"]=rerelate_price_policy_obj

        res = {"error_no": 0, "data": data}
        print("haha",res)

        # 删除数据库中所有的键值
        # r.delete(*r.keys())
        # return Response(request.data)

        # data["total"] =

        # return  Response(json.loads(r.get("shoppingcar_1_*")))

        return Response(res)
    def post(self,request):
        print(request.data)
        """
        状态码:
            1000:成功
            1001:课程不存在
            1002:价格策略错误
        :return:

        模拟请求数据
        {
        "course_id":1,
        "prcie_policy_id":2
        }
        """
        # 1.获取请求数据
        course_id = request.data.get("course_id")
        price_policy_id = request.data.get("price_policy_id")

        # 在liginAuth 里面讲
        user_id = request.user.pk
        # 实例化一个响应类
        res = BaseResponse()


        # 2 校验数据(这里yuan先生try的,)

        '''
        我这样写有很多分支,而且还得总返回一个字典,yuan先生抛异常这个好,学习
        '''
        # if course_id not in [obj.pk for obj in Course.objects.all()]:
        #     res.code=1001auth_permission
        #     res.data="课程不存在"
        #
        # else:
        try:
            # 2.1效验课程数据
            course_obj = Course.objects.get(pk=course_id)
            # 2.2 效验价格策略数据
            price_policy_dict = {}
            for price_policy in course_obj.price_policy.all():
                price_policy_dict[price_policy.pk]={
                    "pk":price_policy.pk,
                    "valid_period":price_policy.valid_period,
                    "valid_period_text":price_policy.get_valid_period_display(),
                    "price":price_policy.price,
                    # 为了前端默认显示
                    "default":int(price_policy_id)==price_policy.pk
                }
                print(price_policy_id, price_policy.pk)
            print(price_policy_dict)
            #  因为有课程策略的替换,而且还有默认值显示 所以需要将价格策略全部存储起来,然后还需要当前价格策略id设置默认显示
            if int(price_policy_id) not in price_policy_dict:
                print(type(price_policy_id))
                print([obj.pk for obj in course_obj.price_policy.all()])

                raise CommonException("1002","价格策略错误")
            price_policy_obj = PricePolicy.objects.filter(pk = price_policy_id).first()
            """
             # 想要购建的数据结构
              REDIS={

                  shoppingcar_1_1:{
                          "title":"....",
                          "img":"...."
                      }

                  shoppingcar_1_2:{
                          "title":"....",
                          "img":"...."
                      }



              }
            """

            # 3 写进redis 中
            # 哪个用户的哪个课程
            pp = PricePolicy.objects.get(pk=price_policy_id)
            shoppingcar_key = settings.SHOPPING_CAR_KEY%(user_id,course_obj.pk)
            shoppingcar_val = {
                "id": course_obj.pk,
                "default_price_period": PricePolicy.objects.filter(pk=price_policy_id).first().valid_period,
                "title":course_obj.name,
                "img":course_obj.course_img,
                "relate_price_policy":price_policy_dict,
                "choose_price_policy_id":price_policy_id,
                "default_price": pp.price,
                "valid_period":price_policy_obj.valid_period,
                "valid_period_text": price_policy_obj.get_valid_period_display(),
            }
            print(shoppingcar_key,shoppingcar_val)
            r.set(shoppingcar_key,json.dumps(shoppingcar_val))





        except CommonException as e:
            res.code = e.code
            res.msg = e.__str__()
        except  ObjectDoesNotExist as e:
            res.code=1001
            res.msg="课程不存在"
        return Response(res.dict)

    # 冯崇版本
    def put(self, request):

            '''
            价格策略更改,价格跟着更改,需要前端传的数据有:课程id,之前的价格策略,新的价格策略
            :param request:
            :return:
            '''
            res = BaseResponse()
            try:
                # 1 获取前端传过来的数据
                courseId = request.data.get('courseId', '')
                newValidPeriodId = request.data.get('newValidPeriodId', '')
                oldValidPeriodId = request.data.get('oldValidPeriodId', '')
                user_id = request.user.id
                # 2 校验数据的合法性
                # 2.1 校验courseId是否合法
                shoppingcar_key = settings.SHOPPING_CAR_KEY % (user_id, courseId)
                if not r.exists(shoppingcar_key):
                    res.error_no = -1
                    res.data = "课程不存在!"
                    return Response(res.dict)
                # 2.2 判断价格策略是否合法
                course_info = json.loads(r.get(shoppingcar_key))  # 从redis数据库中获取当前用户,当前课程的课程信息,为一个字典
                old_price_policy = Course.objects.get(pk=courseId, price_policy__valid_period=oldValidPeriodId)
                new_price_policy = Course.objects.get(pk=courseId, price_policy__valid_period=newValidPeriodId)
                if not old_price_policy and not new_price_policy:
                    res.error_no = -2
                    res.data = "所选的价格策略不存在!"
                    return Response(res.dict)
                price_policy_obj = PricePolicy.objects.get(content_type_id=14, object_id=courseId,
                                                           valid_period=newValidPeriodId)
                course_info['default_price'] = price_policy_obj.price
                course_info['valid_period_text'] = price_policy_obj.get_valid_period_display()
                course_info['valid_period'] = newValidPeriodId
                course_obj = Course.objects.get(pk=courseId)
                # 重新构建数据

                price_policy_dict = {}
                for price_policy in course_obj.price_policy.all():
                    price_policy_dict[price_policy.pk] = {
                        "pk": price_policy.pk,
                        "valid_period": price_policy.valid_period,
                        "valid_period_text": price_policy.get_valid_period_display(),
                        "price": price_policy.price,
                        # 为了前端默认显示
                        "default":  price_policy.valid_period == newValidPeriodId

                    }
                print("===================",price_policy_dict)
                course_info['relate_price_policy'] = price_policy_dict
                r.set(shoppingcar_key, json.dumps(course_info))
                res.data = course_info
                print(res.data)
            except Exception as e:
                res.error_no = -3
                res.data = "更新价格策略失败!"
            return Response(res.dict)


    # def put(self, request):
    #     res = BaseResponse()
    #     try:
    #         # 1 获取前端传过来的course_id 以及price_policy_id
    #         course_id = request.data.get("courseId", "")
    #         newValidPeriodId = request.data.get("newValidPeriodId", "")
    #         oldValidPeriodId = request.data.get("oldValidPeriodId", "")
    #         user_id = request.user.id
    #         print(course_id,newValidPeriodId,oldValidPeriodId)
    # #         # 2 校验数据的合法性
    # #         # 2.1 校验course_id是否合法
    #         shopping_car_key = settings.SHOPPINGCAR_KEY % (user_id, course_id)
    #         print(shopping_car_key)
    #         if not r.exists(shopping_car_key):
    #             res.code = 1035
    #             res.error = "课程不存在"
    #             return Response(res.dict)
    # #         # 2.2 判断价格策略是否合法
    # #
    #         course_info = r.get(shopping_car_key)
    #         print("course_info",course_info)
    #         ret = json.loads(course_info)["relate_price_policy"]
    #         print("relate_price_policy",ret)
    #
    #         for key,value in list(ret.items()):
    #             value["default"] = False
    #             print(type(value["valid_period"]),value["valid_period"],newValidPeriodId)
    #             if int(newValidPeriodId) == value["valid_period"]:
    #                 json.loads(course_info)["default_price_period"] = int(newValidPeriodId)
    #                 print("修改之后的默认有效期",json.loads(r.get(shopping_car_key))["default_price_period"])
    #                 r.set(shopping_car_key, json.dumps(course_info))
    #                 print("更新之后的",json.loads(r.get(shopping_car_key)))
    #                 value["default"] = True
    #                 res.data = "更新成功"
    #                 return Response(res.dict)
    #         else:
    #             res.code = 1036
    #             res.msg = "所选的价格策略不存在"
    #
    #         print(course_info,"yuan")
    #         r.set(shopping_car_key, json.dumps(course_info))
    #         return Response(res.dict)
    # #
    # # #         # if str(price_policy_id) not in price_policy_dict:
    # # #         #     res.code = 1036
    # # #         #     res.error = "所选的价格策略不存在"
    # # #         #     return Response(res.dict)
    # # #         # # 3 修改redis中的default_policy_id
    # # #         # course_info["default_policy_id"] = price_policy_id
    # # #         # # 4 修改信息后写入redis
    # # #         # REDIS_CONN.hmset(shopping_car_key, course_info)
    # # #
    #     except ArithmeticError as e:
    #         res.code = 1034
    #         res.error = "更新价格策略失败"
    #     print(res.dict)
    #     print()
    #     return Response(res.dict)

    #  yuan 先生版本
    # def put(self, request):
    #     res = BaseResponse()
    #     try:
    #         # 1 获取前端传过来的course_id 以及price_policy_id
    #         course_id = request.data.get("course_id", "")
    #         price_policy_id = request.data.get("price_policy_id", "")
    #         user_id = request.user.id
    #         # 2 校验数据的合法性
    #         # 2.1 校验course_id是否合法
    #         shopping_car_key = settings.SHOPPINGCAR_KEY % (user_id, course_id)
    #         if not r.exists(shopping_car_key):
    #             res.code = 1035
    #             res.error = "课程不存在"
    #             return Response(res.dict)
    #         # 2.2 判断价格策略是否合法
    #         course_info = r.hgetall(shopping_car_key)
    #         price_policy_dict = json.loads(course_info["price_policy_dict"])
    #         if str(price_policy_id) not in price_policy_dict:
    #             res.code = 1036
    #             res.error = "所选的价格策略不存在"
    #             return Response(res.dict)
    #         # 3 修改redis中的default_policy_id
    #         course_info["default_policy_id"] = price_policy_id
    #         # 4 修改信息后写入redis
    #         r.hmset(shopping_car_key, course_info)
    #         res.data = "更新成功"
    #     except Exception as e:
    #         res.code = 1034
    #         res.error = "更新价格策略失败"
    #     return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        try:
            # 获取前端传过来的course_id
            course_id = request.data.get("course_id", "")
            user_id = request.user.id
            # 判断课程id是否合法
            shopping_car_key = settings.SHOPPING_CAR_KEY % (user_id, course_id)
            if not r.exists(shopping_car_key):
                res.code = 1039
                res.error = "删除的课程不存在"
                return Response(res.dict)
            # 删除redis中的数据
            r.delete(shopping_car_key)
            res.data = "删除成功"
        except Exception as e:
            res.code = 1037
            res.error = "删除失败"
        return Response(res.dict)
