#!/usr/bin/env python
# -*- coding:utf-8 -*-


def float_compare(x, y):
    '''Helper function to check that two numbers are equal within float precision.'''
    if(y == 0):
        return x == 0
    if(abs((x - y) / y) < 1e-8):
        return True
    return False


def tuple_compare(x, y):
    '''Helper function to check that two tuples are equal within float precision.'''
    return (float_compare(x[0], y[0]) and float_compare(x[1], y[1]))
