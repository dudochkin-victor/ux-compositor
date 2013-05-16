TARGET = focus-tracker

target.path=/usr/bin

QMAKE_CFLAGS+= -Wall

LIBS += -lX11 -lXm

DEPENDPATH += .
INCLUDEPATH += .  

QT -= gui core

SOURCES += focus-tracker.c

INSTALLS +=  \
        target
