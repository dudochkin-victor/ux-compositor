/***************************************************************************
**
** Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
** All rights reserved.
** Contact: Nokia Corporation (directui@nokia.com)
**
** This file is part of mcompositor.
**
** If you have questions regarding the use of this file, please contact
** Nokia at directui@nokia.com.
**
** This library is free software; you can redistribute it and/or
** modify it under the terms of the GNU Lesser General Public
** License version 2.1 as published by the Free Software Foundation
** and appearing in the file LICENSE.LGPL included in the packaging
** of this file.
**
****************************************************************************/

#ifndef DUICOMPOSITEMANAGER_H
#define DUICOMPOSITEMANAGER_H

#include <QApplication>
#include <QGLWidget>
#include <QDir>
#include "mwindowpropertycache.h"

class QGraphicsScene;
class MCompositeManagerPrivate;
class MCompAtoms;
class MCompositeWindow;

/*!
 * MCompositeManager is responsible for managing window events.
 *
 * It catches and redirects appropriate windows to offscreen pixmaps and
 * creates a MTexturePixmapItem object from these windows and adds them
 * to a QGraphicsScene. The manager also ensures the items are updated
 * when their contents change and removes them from its control when they are
 * destroyed.
 *
 */
class MCompositeManager: public QApplication
{
    Q_OBJECT
public:

    /*!
     * Initializes the compositing manager
     *
     * \param argc number of arguments passed from the command line
     * \param argv argument of strings passed from the command line
     */
    MCompositeManager(int &argc, char **argv);

    /*!
     * Cleans up resources
     */
    ~MCompositeManager();

    /*! Prepare and start composite management. This function should get called
     * after the window of this compositor is created and mapped to the screen
     */
    void prepareEvents();

    /*! Specify the QGLWidget used by the QGraphicsView to draw the items on
     * the screen.
     *
     * \param glw The QGLWidget widget used in used by the scene's
     * QGraphicsView viewport
     */
    void setGLWidget(QGLWidget *glw);

    /*! QGLWidget accessor for static initialisations. */
    QGLWidget *glWidget() const;

    /*!
     * Reimplemented from QApplication::x11EventFilter() to catch X11 events
     */
    virtual bool x11EventFilter(XEvent *event);

    /*!
     * Returns the scene where the items are rendered
     */
    QGraphicsScene *scene();

    /*!
     * Specifies the toplevel window where the items are rendered. This window
     * will reparented to the composite overlay window to ensure the compositor
     * stays on top of all windows.
     *
     * \param window Window id of the toplevel window where the items are
     * rendered. Typically, this will be the window id of a toplevel
     * QGraphicsView widget where the items are drawn
     */
    void setSurfaceWindow(Qt::HANDLE window);

    /*!
     * Redirects and manages existing windows as composited items
     */
    void redirectWindows();

    /*!
     * Load @overridePluginPath if provided and abort if fails.
     * Otherwise, if there's no @overridePluginPath loads plugins
     * from @regularPluginDir but skips non-library files and
     * does not abort if there aren't plugins.
     */
    void loadPlugins(const QString &overridePluginPath,
                     const QString &regularPluginDir);

    /*!
     * Returns whether a Window is redirected or not
     *
     * \param w Window id of a window
     */
    bool isRedirected(Qt::HANDLE window);
    
    /*
     * Returns the current state of windows whether it is being composited
     * or not
     */
    bool isCompositing();

    /*!
     * Try to direct-render the topmost window
     */
    bool possiblyUnredirectTopmostWindow();
    
    /*!
     * Returns if the display is off
     */
    bool displayOff();

    void debug(const QString& d);
    const QHash<Window, MWindowPropertyCache*>& propCaches() const;

    enum StackPosition {
        STACK_BOTTOM = 0,
        STACK_TOP
    };
    void positionWindow(Window w, StackPosition pos);
    void setWindowState(Window, int);
    const QList<Window> &stackingList() const;
    Window getLastVisibleParent(MWindowPropertyCache *pc) const;

#ifdef WINDOW_DEBUG
    // Dump the current state of MCompositeManager and MCompositeWindow:s
    // to qDebug().  Only available if compiled with TESTABILITY=on
    // (-DWINDOW_DEBUG).
    void dumpState(const char *heading = 0);

    // "Print" @msg in xtrace, to show you where your program's control was
    // between the various X requests, responses and events.
    // Synopsis:
    // [1] MCompositeManager::xtrace();
    // [2] MCompositeManager::xtrace("HEI");
    // [3] MCompositeManager::xtrace(__PRETTY_FUNCTION__, "HEI");
    //
    // xtracef() is the same, except that it sends a formatted message.
    // You can leave @fun NULL if you want.
    static void xtrace (const char *fun = NULL, const char *msg = NULL,
                        int lmsg = -1);
    static void xtracef(const char *fun, const char *fmt, ...)
        __attribute__((format(printf, 2, 3)));
#endif

public slots:
    void enableCompositing(bool forced = false);
    void disableCompositing();
    // called with the answer to mdecorator's dialog
    void queryDialogAnswer(unsigned int window, bool yes_answer);

    /*! Invoked remotely by MRmiClient to show a launch indicator
     *
     * \param timeout seconds elapsed to hide the launch indicator in case
     * window does not yet appear.
     */
    void showLaunchIndicator(int timeout);
    void hideLaunchIndicator();

    /*!
     * Invoke to show the desktop window, possibly with switcher contents
     */
    void exposeSwitcher();

    /*!
     * Returns the decorator window or NULL.
     */
    MCompositeWindow *decoratorWindow() const;

    /*!
     * Area that is free after the area that decorator occupies.
     */
    const QRect &availableRect() const;

#ifdef WINDOW_DEBUG
    void remoteControl(int fd);
#endif
     
signals:
    void decoratorRectChanged(const QRect& rect);

private:
    MCompositeManagerPrivate *d;

    friend class MCompositeWindow;
    friend class MCompWindowAnimator;
    friend class MCompositeManagerExtension;
    friend class MTexturePixmapPrivate;
    friend class MWindowPropertyCache;
    friend class MCompositeWindowGroup;
};

#endif
